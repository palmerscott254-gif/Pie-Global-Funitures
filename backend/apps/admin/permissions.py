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


class HasRole(BasePermission):
    """Permission that checks the user's role against view.required_roles.

    Views may set ``required_roles = ['staff_admin', 'support_agent']`` to
    restrict access to specific role names. Superusers bypass role checks.
    If ``required_roles`` is not defined on the view, falls back to
    `IsAdminOrStaff` behavior.
    """

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user and getattr(user, 'is_authenticated', False)):
            return False

        # Superusers always allowed
        if getattr(user, 'is_superuser', False):
            return True

        required = getattr(view, 'required_roles', None)
        if not required:
            # default to staff check when no specific roles declared
            return bool(getattr(user, 'is_staff', False))

        # allow if user's role matches any required role
        user_role = getattr(user, 'role', None)
        return bool(user_role and user_role in required)
