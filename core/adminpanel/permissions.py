from rest_framework.permissions import BasePermission


class IsAdminPanelUser(BasePermission):
    # permitem accesul doar utilizatorilor autentificati care sunt admini
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )