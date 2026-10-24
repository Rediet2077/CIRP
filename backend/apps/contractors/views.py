import uuid
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StaffContractor
from .serializers import StaffContractorSerializer, CreateStaffContractorSerializer
from apps.tasks.models import Task
from apps.tasks.serializers import TaskSerializer
from utils.permissions import IsStaffOrAdminUser
from utils.responses import api_response


def get_contractor_or_404(pk):
    """Gracefully resolve StaffContractor by UUID."""
    try:
        val_uuid = uuid.UUID(str(pk))
        return get_object_or_404(StaffContractor.objects.select_related('department'), id=val_uuid)
    except (ValueError, TypeError):
        return get_object_or_404(StaffContractor.objects.select_related('department'), id=pk)


class ContractorListCreateView(APIView):
    """
    List and provision staff officers and contractors.
    - GET: Filter by department_id. Scoped by department.
    - POST: Provision new worker or contractor team.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, *args, **kwargs):
        user = request.user
        queryset = StaffContractor.objects.select_related('department').all()

        # Department scoping
        if not user.is_system_admin and user.department:
            queryset = queryset.filter(department=user.department)

        dept_id = request.query_params.get('department_id') or request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)

        serializer = StaffContractorSerializer(queryset, many=True)
        return api_response(serializer.data, request=request)

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = CreateStaffContractorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        target_dept = serializer.validated_data['department_id']
        if not user.is_system_admin and target_dept != user.department:
            return Response(
                {"detail": "You cannot provision staff/contractors outside your assigned department."},
                status=status.HTTP_403_FORBIDDEN
            )

        worker = serializer.save()
        output_serializer = StaffContractorSerializer(worker)
        return api_response(
            output_serializer.data,
            message="Contractor/staff profile created successfully.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class ContractorDetailView(APIView):
    """
    Retrieve single contractor or staff profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, pk, *args, **kwargs):
        worker = get_contractor_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and worker.department != user.department:
                return Response(
                    {"detail": "You cannot view workers outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        serializer = StaffContractorSerializer(worker)
        return api_response(serializer.data, request=request)


class ContractorTasksView(APIView):
    """
    List tasks assigned to a specific contractor.
    """
    permission_classes = [permissions.IsAuthenticated, IsStaffOrAdminUser]

    def get(self, request, pk, *args, **kwargs):
        worker = get_contractor_or_404(pk)
        user = request.user

        if not user.is_system_admin:
            if user.department and worker.department != user.department:
                return Response(
                    {"detail": "You cannot view tasks outside your assigned department."},
                    status=status.HTTP_403_FORBIDDEN
                )

        tasks = Task.objects.filter(
            assigned_worker=worker
        ).select_related(
            'department', 'report', 'report__asset', 'report__asset__asset_type', 'assigned_worker'
        ).prefetch_related('extensions').all()

        serializer = TaskSerializer(tasks, many=True)
        return api_response(serializer.data, request=request)
