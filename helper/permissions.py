from rest_framework.permissions import BasePermission

class HaveRole(BasePermission):
    message = 'User Does not have required role to perform this action.'

    def has_permission(self, request, view):
        return request.user.role == view.required_role

class IsOwnerOrNoAccess(BasePermission):
    message = 'User is not the owner of this object'

    def has_object_permission(self, request, view, obj):
        user = request.user
        # check if created_by field is present otherwise 
        # check against user field
        if hasattr(obj, 'created_by'):
            return obj.created_by == user
        return obj.user == user