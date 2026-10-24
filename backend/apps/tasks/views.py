import uuid
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Task
from .serializers import (
    TaskSerializer,
    UpdateTaskProgressSerializer,
    SubmitTaskCompletionSerializer,
    VerifyResolveTaskSerializer,
    ReturnRejectTaskSerializer,
    TaskReassignUpdateSerializer,
)
from apps.reports.models import Report
from utils.enums import TaskStatus, ReportStatus, UserRole
from utils.permissions import IsStaffOrAdminUser
from utils.responses import api_response


def get_task_or_404(pk):
    """Gracefully resolve Task by UUID or task_code."""
    qs = Task.objects.select_related(
        'department', 'report', 'report__asset', 'report__asset__asset_type', 'assigned_worker'
    ).prefetch_related('extensions')
    try:
        val_uuid = uuid.UUID(str(pk))
        return get_object_or_404(qs, id=val_uuid)
    except (ValueError, TypeError):
        return get_object_or_404(qs, task_code=str(pk))


class TaskListCreateView(APIView):
    """
    List municipal operational tasks.
    - Scoped by department.
    - Filterable by department_id, status, assigned_worker_id, search query, overdue.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Task.objects.select_related(
            'department', 'report', 'report__asset', 'report__asset__asset_type', 'assigned_worker'
        ).prefetch_related('extensions').all()

        # Department scoping
        if not user.is_system_admin and user.department:
            queryset = queryset.filter(department=user.department)

        # Filters
        dept_id = request.query_params.get('department_id') or request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)

        task_status = request.query_params.get('status')
        if task_status:
            queryset = queryset.filter(status__iexact=task_status)

        worker_id = request.query_params.get('assigned_worker_id') or request.query_params.get('worker_id')
        if worker_id:
            queryset = queryset.filter(assigned_worker_id=worker_id)

        search_query = request.query_params.get('search') or request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(task_code__icontains=search_query) |
                Q(report__report_code__icontains=search_query) |
                Q(report__title__icontains=search_query) |
                Q(report__description__icontains=search_query) |
                Q(work_description__icontains=search_query) |
                Q(assigned_worker__name__icontains=search_query)
            )

        overdue_filter = request.query_params.get('overdue')
        if overdue_filter and overdue_filter.lower() in ('true', '1'):
            queryset = queryset.filter(
                deadline_date__lt=timezone.now()
            ).exclude(status__in=[TaskStatus.RESOLVED, TaskStatus.VERIFIED])

        serializer = TaskSerializer(queryset, many=True)
        return api_response(serializer.data, request=request)


class TaskDetailView(APIView):
    """
    Retrieve single task details or reassign/update task attributes.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot view tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = TaskSerializer(task)
        return api_response(serializer.data, request=request)

    def patch(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot modify tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = TaskReassignUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            notes = list(task.progress_notes or [])
            officer_name = user.get_full_name() or user.email

            # Handle worker reassignment
            if 'resolved_worker' in data and data['resolved_worker']:
                new_worker = data['resolved_worker']
                if not user.is_system_admin and new_worker.department != task.department:
                    return Response(
                        {"detail": "Newly assigned worker belongs to a different department."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                old_worker_name = task.assigned_worker.name if task.assigned_worker else "Unassigned"
                task.assigned_worker = new_worker
                notes.append({
                    "timestamp": timezone.now().isoformat(),
                    "author": officer_name,
                    "note": f"Task reassigned from {old_worker_name} to {new_worker.name}.",
                    "percentage": task.progress_percentage,
                })

            if data.get('resolved_priority'):
                task.priority = data['resolved_priority']
            if data.get('resolved_work_desc'):
                task.work_description = data['resolved_work_desc']
            if data.get('resolved_internal_note') is not None:
                task.internal_note = data['resolved_internal_note']
            if data.get('resolved_deadline'):
                task.deadline_date = data['resolved_deadline']

            task.progress_notes = notes
            task.save()

        output_serializer = TaskSerializer(task)
        return api_response(output_serializer.data, message="Task updated successfully.", request=request)


class TaskProgressView(APIView):
    """
    Record progress update, percentage, and audit progress note.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot update tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        if task.status in [TaskStatus.RESOLVED, TaskStatus.VERIFIED]:
            return Response(
                {"detail": "Cannot update progress on already resolved tasks."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateTaskProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        pct = data['resolved_percentage']
        new_status = data['resolved_status']
        note = data['resolved_note']
        author = data['resolved_author']

        with transaction.atomic():
            notes = list(task.progress_notes or [])
            notes.append({
                "timestamp": timezone.now().isoformat(),
                "author": author,
                "note": note,
                "percentage": pct,
            })

            task.progress_percentage = pct
            task.status = new_status
            task.progress_notes = notes
            task.save(update_fields=['progress_percentage', 'status', 'progress_notes', 'updated_at'])

            # Sync related Report status if moving to IN_PROGRESS
            if new_status == TaskStatus.IN_PROGRESS and task.report and task.report.status != ReportStatus.IN_PROGRESS:
                task.report.status = ReportStatus.IN_PROGRESS
                task.report.save(update_fields=['status', 'updated_at'])

        output_serializer = TaskSerializer(task)
        return api_response(output_serializer.data, message="Progress recorded successfully.", request=request)


class TaskCompletionView(APIView):
    """
    Contractor completion submission endpoint:
    - Uploads before/after photos and completion notes.
    - Sets task status to COMPLETED_PENDING_VERIFICATION.
    - Sets report status to COMPLETED_PENDING_VERIFICATION.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot submit completion for tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = SubmitTaskCompletionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        with transaction.atomic():
            task.completion_submission = {
                "completion_notes": data['resolved_notes'],
                "completion_date": data['resolved_date'],
                "submitted_by": data['resolved_submitter'],
                "before_photos": data['resolved_before_photos'],
                "after_photos": data['resolved_after_photos'],
            }
            task.status = TaskStatus.COMPLETED_PENDING_VERIFICATION
            task.progress_percentage = 100

            notes = list(task.progress_notes or [])
            notes.append({
                "timestamp": timezone.now().isoformat(),
                "author": data['resolved_submitter'],
                "note": f"Work completed and submitted for verification: {data['resolved_notes']}",
                "percentage": 100,
            })
            task.progress_notes = notes
            task.save(update_fields=['completion_submission', 'status', 'progress_percentage', 'progress_notes', 'updated_at'])

            if task.report:
                task.report.status = ReportStatus.COMPLETED_PENDING_VERIFICATION
                task.report.save(update_fields=['status', 'updated_at'])

        output_serializer = TaskSerializer(task)
        return api_response(output_serializer.data, message="Completion submitted for verification.", request=request)


class TaskVerifyResolveView(APIView):
    """
    Administrative sign-off:
    - Verifies completed work on site.
    - Sets task status to RESOLVED and records resolved_at.
    - Sets report status to RESOLVED and records resolution notes.
    - Returns boolean true.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot verify tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = VerifyResolveTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        officer = data['resolved_officer']
        notes = data['resolved_notes']
        now = timezone.now()

        with transaction.atomic():
            task.status = TaskStatus.RESOLVED
            task.resolved_at = now
            task.progress_percentage = 100

            p_notes = list(task.progress_notes or [])
            p_notes.append({
                "timestamp": now.isoformat(),
                "author": officer,
                "note": f"Verified and resolved: {notes}",
                "percentage": 100,
            })
            task.progress_notes = p_notes
            task.save(update_fields=['status', 'resolved_at', 'progress_percentage', 'progress_notes', 'updated_at'])

            if task.report:
                task.report.status = ReportStatus.RESOLVED
                task.report.resolved_at = now
                task.report.resolution_notes = f"[{officer}]: {notes}"
                task.report.save(update_fields=['status', 'resolved_at', 'resolution_notes', 'updated_at'])

        return api_response(True, message="Task verified and marked as resolved.", request=request)


class TaskReturnRejectView(APIView):
    """
    Administrative rejection / rework return:
    - Substandard work returned to contractor.
    - Sets task status to RETURNED and extends new expected date.
    - Records in rejection_history and progress_notes.
    - Sets report status back to IN_PROGRESS.
    - Returns boolean true.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        task = get_task_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot return tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = ReturnRejectTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        officer = data['resolved_officer']
        reason = data['reason']
        correction = data['resolved_correction']
        new_date = data['resolved_new_date']
        now = timezone.now()

        with transaction.atomic():
            task.status = TaskStatus.RETURNED
            task.deadline_date = new_date
            task.progress_percentage = 75

            # Append to rejection history
            r_history = list(task.rejection_history or [])
            r_history.append({
                "timestamp": now.isoformat(),
                "rejected_by": officer,
                "reason": reason,
                "required_correction": correction,
                "new_expected_date": new_date.isoformat(),
            })
            task.rejection_history = r_history

            # Append to progress notes
            p_notes = list(task.progress_notes or [])
            p_notes.append({
                "timestamp": now.isoformat(),
                "author": officer,
                "note": f"Work returned for correction. Reason: {reason}. Required: {correction}. New expected date: {new_date.strftime('%Y-%m-%d %H:%M')}",
                "percentage": 75,
            })
            task.progress_notes = p_notes
            task.save(update_fields=['status', 'deadline_date', 'progress_percentage', 'rejection_history', 'progress_notes', 'updated_at'])

            if task.report:
                task.report.status = ReportStatus.IN_PROGRESS
                task.report.save(update_fields=['status', 'updated_at'])

        return api_response(True, message="Task returned for correction.", request=request)
