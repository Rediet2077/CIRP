from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.users.serializers import UserSerializer

from .models import Department
from .permissions import IsDepartmentAdmin
from .serializers import DepartmentSerializer

User = get_user_model()


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('admin_user').all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsDepartmentAdmin]
    
    def get_queryset(self):
        """
        Filter departments based on approval status
        """
        queryset = Department.objects.select_related('admin_user', 'approved_by').all()
        
        # Filter by approval status if provided
        approval_status = self.request.query_params.get('approval_status', None)
        if approval_status:
            queryset = queryset.filter(approval_status=approval_status)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Register new department - starts as PENDING approval
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # New departments start as PENDING
        department = serializer.save(approval_status=Department.ApprovalStatus.PENDING)
        
        return Response({
            'success': True,
            'message': 'Department registration submitted. Waiting for admin approval.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='pending-approvals')
    def pending_approvals(self, request):
        """
        Get list of departments waiting for approval (New Applicants)
        Only accessible by SYSTEM_ADMIN
        """
        if not request.user.is_superuser and request.user.role != 'SYSTEM_ADMIN':
            return Response({
                'error': 'Only system administrators can view pending approvals'
            }, status=status.HTTP_403_FORBIDDEN)
        
        pending_departments = Department.objects.filter(
            approval_status=Department.ApprovalStatus.PENDING
        ).order_by('-created_at')
        
        serializer = self.get_serializer(pending_departments, many=True)
        return Response({
            'success': True,
            'message': f'Found {pending_departments.count()} pending department approvals',
            'data': serializer.data,
            'count': pending_departments.count()
        })
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_department(self, request, pk=None):
        """
        Approve a pending department registration
        Only accessible by SYSTEM_ADMIN
        """
        if not request.user.is_superuser and request.user.role != 'SYSTEM_ADMIN':
            return Response({
                'error': 'Only system administrators can approve departments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        department = self.get_object()
        
        if department.approval_status != Department.ApprovalStatus.PENDING:
            return Response({
                'error': f'Department is already {department.get_approval_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Approve the department
        department.approval_status = Department.ApprovalStatus.APPROVED
        department.approved_by = request.user
        department.approved_at = timezone.now()
        department.is_active = True
        department.save()
        
        return Response({
            'success': True,
            'message': f'Department "{department.name}" has been approved and can now access the platform',
            'data': DepartmentSerializer(department).data
        })
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject_department(self, request, pk=None):
        """
        Reject a pending department registration
        Only accessible by SYSTEM_ADMIN
        """
        if not request.user.is_superuser and request.user.role != 'SYSTEM_ADMIN':
            return Response({
                'error': 'Only system administrators can reject departments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        department = self.get_object()
        reason = request.data.get('reason', 'No reason provided')
        
        if department.approval_status != Department.ApprovalStatus.PENDING:
            return Response({
                'error': f'Department is already {department.get_approval_status_display()}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reject the department
        department.approval_status = Department.ApprovalStatus.REJECTED
        department.rejection_reason = reason
        department.approved_by = request.user
        department.approved_at = timezone.now()
        department.is_active = False
        department.save()
        
        return Response({
            'success': True,
            'message': f'Department "{department.name}" has been rejected',
            'reason': reason,
            'data': DepartmentSerializer(department).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete/remove a department
        Only accessible by SYSTEM_ADMIN
        """
        if not request.user.is_superuser and request.user.role != 'SYSTEM_ADMIN':
            return Response({
                'error': 'Only system administrators can delete departments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        department = self.get_object()
        department_name = department.name
        
        # Check if department has active tasks/reports
        if department.tasks.filter(status__in=['PENDING', 'IN_PROGRESS']).exists():
            return Response({
                'error': 'Cannot delete department with active tasks. Please reassign or complete them first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        department.delete()
        
        return Response({
            'success': True,
            'message': f'Department "{department_name}" has been removed'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='staff')
    def list_staff(self, request, pk=None):
        """List the user currently assigned as the department administrator."""
        department = self.get_object()
        staff_users = User.objects.filter(pk=department.admin_user_id)
        serializer = UserSerializer(staff_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='assign-staff')
    def assign_staff(self, request, pk=None):
        """Assign a user as the department administrator."""
        department = self.get_object()
        user_id = request.data.get('user_id')

        if not user_id:
            return Response(
                {"error": "'user_id' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        department.admin_user = user
        department.save(update_fields=['admin_user', 'updated_at'])
        return Response({"message": f"User '{user.email}' assigned to {department.name} successfully."})

    @action(detail=True, methods=['get'], url_path='overview')
    def department_overview(self, request, pk=None):
        """Return task statistics for the department dashboard."""
        department = self.get_object()
        tasks = department.tasks

        data = {
            "department_id": department.id,
            "department_name": department.name,
            "total_tasks": tasks.count(),
            "pending_tasks": tasks.filter(status='PENDING').count(),
            "in_progress_tasks": tasks.filter(status='IN_PROGRESS').count(),
            "completed_tasks": tasks.filter(status='COMPLETED_PENDING_VERIFICATION').count(),
        }
        return Response(data, status=status.HTTP_200_OK)