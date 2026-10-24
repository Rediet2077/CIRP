from rest_framework import generics, filters, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from utils.responses import api_response, error_response
from utils.permissions import IsSystemAdmin, IsDepartmentAdmin
from .models import Department
from .serializers import DepartmentSerializer


class IsDepartmentAdminOrSystemAdminForObject(permissions.BasePermission):
    """
    Object-level permission allowing:
    - System Admins to update any department.
    - Department Admins to update only their own department.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.role == 'SYSTEM_ADMIN':
            return True
        if request.user.role == 'DEPARTMENT_ADMIN' and request.user.department == obj:
            return True
        return False


class DepartmentListView(generics.ListAPIView):
    """
    List municipal departments and their operational KPI metrics.
    GET /api/v1/departments/ and GET /departments
    """
    permission_classes = [AllowAny]
    queryset = Department.objects.filter(is_active=True).order_by('name')
    serializer_class = DepartmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            data=serializer.data,
            message="Departments retrieved successfully.",
            request=request
        )


class DepartmentDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a specific department profile.
    GET /api/v1/departments/<uuid>/
    PATCH /api/v1/departments/<uuid>/
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsDepartmentAdminOrSystemAdminForObject()]
        return [AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            data=serializer.data,
            message="Department retrieved successfully.",
            request=request
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return api_response(
            data=serializer.data,
            message="Department updated successfully.",
            request=request
        )
