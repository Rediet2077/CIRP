import uuid
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Report
from .serializers import (
    CitizenReportCreateSerializer,
    ReportSerializer,
    AcceptReportSerializer,
    RejectReportSerializer,
    LinkAssetSerializer,
    PublicReportSerializer,
)
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from utils.enums import ReportStatus, TaskPriority, TaskStatus, UserRole
from utils.permissions import IsCitizenUser, IsStaffOrAdminUser
from utils.responses import api_response


def get_report_or_404(pk, select_related_fields=None, **extra_kwargs):
    """Gracefully resolves Report by UUID or by human-readable report_code."""
    qs = Report.objects.all()
    if select_related_fields:
        qs = qs.select_related(*select_related_fields)
    try:
        val_uuid = uuid.UUID(str(pk))
        return get_object_or_404(qs, id=val_uuid, **extra_kwargs)
    except (ValueError, TypeError):
        return get_object_or_404(qs, report_code=pk, **extra_kwargs)


class ReportListCreateView(APIView):
    """
    Dual-purpose view:
    - GET: Admin report list, filterable by department, status, and search query.
      Ordinary citizens only see their own submitted reports.
    - POST: Citizen incident submission supporting photos, GPS, and categories.
    """
    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Report.objects.filter(is_deleted_by_admin=False).select_related(
            'category', 'department', 'asset', 'asset__asset_type', 'citizen'
        )

        # Role-based scoping: Citizens only see their own active reports
        if getattr(user, 'role', None) == UserRole.CITIZEN:
            queryset = queryset.filter(citizen=user, is_deleted_by_citizen=False)
        elif getattr(user, 'role', None) == UserRole.DEPARTMENT_ADMIN:
            # Department admin is scoped to their department unless superuser
            if not user.is_system_admin and user.department:
                queryset = queryset.filter(department=user.department)

        # Admin query parameter filtering
        dept_id = request.query_params.get('department_id') or request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)

        rep_status = request.query_params.get('status')
        if rep_status:
            # In frontend, "DISPUTED" or "REJECTED" may be requested
            if rep_status.upper() in ['DISPUTED', 'REJECTED']:
                queryset = queryset.filter(status__in=[ReportStatus.DISPUTED, ReportStatus.REJECTED])
            else:
                queryset = queryset.filter(status__iexact=rep_status)

        search_query = request.query_params.get('search') or request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        serializer = ReportSerializer(queryset, many=True)
        return api_response(serializer.data, request=request)

    def post(self, request, *args, **kwargs):
        serializer = CitizenReportCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        report = serializer.save()

        # Format created report matching frontend expectations
        output_serializer = ReportSerializer(report)
        return api_response(
            output_serializer.data,
            message="Report submitted successfully.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class CitizenMyReportsView(generics.ListAPIView):
    """
    List reports submitted by the authenticated citizen.
    Used by Flutter's My Reports screen.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(
            citizen=self.request.user,
            is_deleted_by_citizen=False
        ).select_related('category', 'department', 'asset', 'citizen').order_by('-submitted_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_response(serializer.data, request=request)


class CitizenReportDeleteView(APIView):
    """
    Soft-delete a report from the citizen's personal history.
    Does not delete the report from administrative audit logs.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        report = get_report_or_404(pk, citizen=request.user)
        report.is_deleted_by_citizen = True
        report.save(update_fields=['is_deleted_by_citizen'])
        return api_response({"success": True}, message="Report removed from your history.", request=request)


class ReportDetailView(APIView):
    """
    Retrieve single report details.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        report = get_report_or_404(
            pk,
            select_related_fields=['category', 'department', 'asset', 'asset__asset_type', 'citizen']
        )

        # Scoping: Citizen can only view their own report
        user = request.user
        if getattr(user, 'role', None) == UserRole.CITIZEN and report.citizen != user:
            return Response(
                {"detail": "You do not have permission to view this report."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Department admin can only view reports in their department
        if getattr(user, 'role', None) == UserRole.DEPARTMENT_ADMIN and not user.is_system_admin:
            if user.department and report.department != user.department:
                return Response(
                    {"detail": "This report does not belong to your department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = ReportSerializer(report)
        return api_response(serializer.data, request=request)


class AcceptReportView(APIView):
    """
    Triage Action: Accept an incident report and generate its operational Task.
    - Enforces department admin or system admin permissions.
    - Transaction atomic and safe to retry without creating duplicate tasks.
    - Returns TaskRecordSchema conforming output for React Admin.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        report = get_report_or_404(pk)
        user = request.user

        # Department permission check
        if not user.is_system_admin:
            if user.department and report.department != user.department:
                return Response(
                    {"detail": "You cannot accept reports outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Validate input payload
        serializer = AcceptReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        worker = data['resolved_worker']
        deadline = data['resolved_deadline']
        work_desc = data['resolved_work_desc']
        internal_note = data['resolved_internal_note']
        priority = data.get('priority', TaskPriority.MEDIUM)

        # Worker must belong to the department
        if worker.department != report.department:
            return Response(
                {"detail": "The assigned worker does not belong to this department."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Check if task already exists for this report
            existing_task = Task.objects.filter(report=report).first()
            if existing_task:
                # Safe idempotent return
                task_serializer = TaskSerializer(existing_task)
                return api_response(task_serializer.data, message="Report already accepted.", request=request)

            # Generate unique task_code: TSK-YYYY-XXXX
            year = datetime.now().year
            rand_suffix = f"{uuid.uuid4().int % 9000 + 1000}"
            task_code = f"TSK-{year}-{rand_suffix}"
            while Task.objects.filter(task_code=task_code).exists():
                rand_suffix = f"{uuid.uuid4().int % 9000 + 1000}"
                task_code = f"TSK-{year}-{rand_suffix}"

            # Create Task
            task = Task.objects.create(
                task_code=task_code,
                report=report,
                department=report.department,
                assigned_worker=worker,
                priority=priority,
                status=TaskStatus.ASSIGNED,
                work_description=work_desc,
                internal_note=internal_note,
                deadline_date=deadline,
                original_deadline_date=deadline,
                progress_percentage=0,
            )

            # Update report status to ACCEPTED
            report.status = ReportStatus.ACCEPTED
            report.save(update_fields=['status', 'updated_at'])

        task_serializer = TaskSerializer(task)
        return api_response(
            task_serializer.data,
            message="Report accepted and operational task created.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class RejectReportView(APIView):
    """
    Triage Action: Reject an incident report.
    - Requires a documented reason (min 5 characters).
    - Updates status to DISPUTED (displayed as REJECTED in React).
    - Logs officer identity and timestamp.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        report = get_report_or_404(pk)
        user = request.user

        # Department permission check
        if not user.is_system_admin:
            if user.department and report.department != user.department:
                return Response(
                    {"detail": "You cannot reject reports outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = RejectReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data['reason']

        # Update report status
        timestamp_str = timezone.now().strftime("%Y-%m-%d %H:%M UTC")
        officer_name = user.get_full_name() or user.email
        rejection_note = f"[{officer_name} on {timestamp_str}]: {reason}"

        report.status = ReportStatus.DISPUTED
        report.rejection_reason = rejection_note
        report.save(update_fields=['status', 'rejection_reason', 'updated_at'])

        output_serializer = ReportSerializer(report)
        return api_response(
            output_serializer.data,
            message="Report rejected successfully.",
            request=request
        )


class LinkAssetView(APIView):
    """
    Triage Action: Link a physical infrastructure asset to a report.
    - Validates asset existence and department match.
    - Returns boolean true to satisfy React Admin outputSchema: z.boolean().
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        report = get_report_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and report.department != user.department:
                return Response(
                    {"detail": "You cannot link assets for reports outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = LinkAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asset = serializer.validated_data['resolved_asset']

        # Asset department check
        if not user.is_system_admin and asset.department != report.department:
            return Response(
                {"detail": "Selected asset belongs to a different department."},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.asset = asset
        report.save(update_fields=['asset', 'updated_at'])

        # Return boolean true (React's z.boolean() expects direct boolean or envelope)
        return api_response(True, message="Asset successfully linked to report.", request=request)


class PublicReportListView(generics.ListAPIView):
    """
    Public Transparency Portal.
    - Anonymous access permitted (AllowAny).
    - Strictly filters out private citizen identity, contact information, internal notes.
    - Conforms to React Admin's PublicReportSchema.strict().
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Report.objects.filter(
            is_deleted_by_citizen=False,
            is_deleted_by_admin=False
        ).select_related('category').order_by('-submitted_at')[:100]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = PublicReportSerializer(queryset, many=True)
        return api_response(serializer.data, request=request)
