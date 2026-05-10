from rest_framework.permissions import BasePermission


class IsAdminOrStaff(BasePermission):
    """
    Allows access only to admin users (is_superuser or is_staff).
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and (
                request.user.is_superuser or
                request.user.is_staff
            )
        )
