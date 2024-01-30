from rest_framework.permissions import BasePermission
from users.models import Manager
from plans.models import IDP


class IsManagerOfEmployee(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            try:
                manager_profile = request.user.manager_profile
                if manager_profile == obj.head:
                    return True
            except Manager.DoesNotExist:
                pass
            if IDP.objects.filter(
                    employee=obj,
                    mentor=request.user.employee_profile).exists():
                return True
            if request.user.employee_profile == obj:
                return True
        return False
