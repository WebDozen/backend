from rest_framework.permissions import BasePermission
from users.models import Manager


class IsManagerOfEmployee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            try:
                manager_profile = request.user.manager_profile
                if manager_profile == obj.head:
                    return True
            except Manager.DoesNotExist:
                pass
            if request.user.employee_profile == obj:
                return True
        return False
