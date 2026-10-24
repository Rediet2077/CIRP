import uuid
from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Extension
from .serializers import (
    ExtensionSerializer,
    RequestExtensionSerializer,
    DecideExtensionSerializer,
)
from utils.enums import TaskExtensionStatus, UserRole
from utils.permissions import IsStaffOrAdminUser
from utils.responses import api_response


def get_extension_or_404(pk):
    """Gracefully resolve Extension by UUID."""
    try:
        val_uuid = uuid.UUID(str(pk))
        return get_object_or_404(Extension.objects.select_related('task', 'task__department', 'task__report'), id=val_uuid)
    except (ValueError, TypeError):
        return get_object_or_404(Extension.objects.select_related('task', 'task__department', 'task__report'), id=pk)


class ExtensionListCreateView(APIView):
    """
    List and create deadline extension requests.
    - GET: Filter by department_id and status.
    - POST: Submit new extension request.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = Extension.objects.select_related(
            'task', 'task__department', 'task__report', 'task__report__asset', 'requested_by', 'decided_by'
        ).all()

        # Department scoping
        if not user.is_system_admin and user.department:
            queryset = queryset.filter(task__department=user.department)

        dept_id = request.query_params.get('department_id') or request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(task__department_id=dept_id)

        ext_status = request.query_params.get('status')
        if ext_status:
            queryset = queryset.filter(status__iexact=ext_status)

        serializer = ExtensionSerializer(queryset, many=True)
        return api_response(serializer.data, request=request)

    def post(self, request, *args, **kwargs):
        serializer = RequestExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        task = data['resolved_task']
        user = request.user

        # Department permission check
        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot request extensions for tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        requester_name = data['resolved_requester_name'] or user.get_full_name() or user.email

        with transaction.atomic():
            ext = Extension.objects.create(
                task=task,
                requested_by=user,
                requested_by_name=requester_name,
                original_deadline=task.deadline_date,
                requested_new_deadline=data['resolved_new_deadline'],
                reason_category=data['resolved_reason_category'],
                detailed_explanation=data['resolved_explanation'],
                supporting_evidence_note=data['resolved_evidence'],
                status=TaskExtensionStatus.PENDING,
            )

            # Record formal extension request into task progress notes
            notes = list(task.progress_notes or [])
            notes.append({
                "timestamp": timezone.now().isoformat(),
                "author": requester_name,
                "note": f"Extension requested to {ext.requested_new_deadline.strftime('%Y-%m-%d %H:%M')}. Reason: {ext.reason_category} - {ext.detailed_explanation}",
                "percentage": task.progress_percentage,
            })
            task.progress_notes = notes
            task.save(update_fields=['progress_notes', 'updated_at'])

        output_serializer = ExtensionSerializer(ext)
        return api_response(
            output_serializer.data,
            message="Deadline extension requested successfully.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class DecideExtensionView(APIView):
    """
    Administrative decision endpoint to approve or reject an extension request.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def post(self, request, pk, *args, **kwargs):
        extension = get_extension_or_404(pk)
        user = request.user
        task = extension.task

        # Department permission check
        if not user.is_system_admin:
            if user.department and task.department != user.department:
                return Response(
                    {"detail": "You cannot decide extensions outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = DecideExtensionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        approve = data['approve']
        decider_name = data['resolved_decider_name'] or user.get_full_name() or user.email
        comment = data['resolved_comment']

        with transaction.atomic():
            notes = list(task.progress_notes or [])
            if approve:
                extension.status = TaskExtensionStatus.APPROVED
                task.deadline_date = extension.requested_new_deadline
                notes.append({
                    "timestamp": timezone.now().isoformat(),
                    "author": decider_name,
                    "note": f"Extension approved to {extension.requested_new_deadline.strftime('%Y-%m-%d %H:%M')}. Note: {comment}",
                    "percentage": task.progress_percentage,
                })
            else:
                extension.status = TaskExtensionStatus.REJECTED
                notes.append({
                    "timestamp": timezone.now().isoformat(),
                    "author": decider_name,
                    "note": f"Extension rejected. Note: {comment}",
                    "percentage": task.progress_percentage,
                })

            extension.decision_date = timezone.now()
            extension.decided_by = user
            extension.decided_by_name = decider_name
            extension.decision_comment = comment
            extension.save(update_fields=['status', 'decision_date', 'decided_by', 'decided_by_name', 'decision_comment', 'updated_at'])

            task.progress_notes = notes
            task.save(update_fields=['deadline_date', 'progress_notes', 'updated_at'])

        # Return boolean true to satisfy React Admin outputSchema: z.boolean()
        return api_response(True, message=f"Extension {'approved' if approve else 'rejected'} successfully.", request=request)
