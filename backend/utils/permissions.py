from rest_framework import permissions
from .enums import UserRole


class IsSystemAdmin(permissions.BasePermission):
    """
    Allows access only to System Admins or Django superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == UserRole.SYSTEM_ADMIN or request.user.is_superuser)
        )


class IsDepartmentAdmin(permissions.BasePermission):
    """
    Allows access to Department Admins and System Admins.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in (UserRole.DEPARTMENT_ADMIN, UserRole.SYSTEM_ADMIN) or request.user.is_superuser)
        )


class IsCitizen(permissions.BasePermission):
    """
    Allows access to registered Citizens.
    """
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.CITIZEN
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission allowing the owner of an entity, or department/system admins, to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.role == UserRole.SYSTEM_ADMIN or request.user.is_superuser:
            return True

        if hasattr(obj, 'citizen') and obj.citizen == request.user:
            return True

        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        if hasattr(obj, 'department') and hasattr(request.user, 'department') and obj.department == request.user.department:
            return True

        return False


# Aliases for backward & domain compatibility
IsStaffOrAdminUser = IsDepartmentAdmin
IsCitizenUser = IsCitizen
