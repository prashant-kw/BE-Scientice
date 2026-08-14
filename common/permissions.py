from rest_framework.permissions import BasePermission

class IsPortalAdmin(BasePermission):
    """
    Strict authorization permission class for administrative endpoints.

    CRITICAL SECURITY ARCHITECTURE RULES:
    1. NEVER read privilege from request.auth / token claims.
       Always check `request.user.is_staff` or `request.user.is_superuser`, which are
       fetched fresh from the database by SimpleJWT's `JWTAuthentication` on every request.
       Reading privilege from token claims introduces a stale-privilege vulnerability
       (e.g., a demoted or revoked admin's still-valid access token retaining access).
    2. `request.user.role` is strictly an identity/display badge and MUST NOT be used
       for authorization decisions. Authorization must always evaluate `is_staff` or `is_superuser`.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )

class IsContentEditor(BasePermission):
    """
    Authorization permission class for Content Management System (CMS) endpoints.
    Allows staff, superusers, or active members of the 'Content Editor' group.
    
    Like IsPortalAdmin, checks are performed live against the database-fetched request.user.
    """
    def has_permission(self, request, view):
        u = request.user
        return bool(
            u and
            u.is_authenticated and
            u.is_active and
            (
                u.is_staff or
                u.is_superuser or
                u.groups.filter(name='Content Editor').exists()
            )
        )

