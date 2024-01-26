from rest_framework.permissions import BasePermission


class IsManagerOfEmployee(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.manager_profile == obj.head
