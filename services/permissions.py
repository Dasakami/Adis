from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'executor', None) or getattr(obj, 'author', None)
        if owner is None:
            return request.user.is_staff 
        return (owner == request.user) or request.user.is_staff
