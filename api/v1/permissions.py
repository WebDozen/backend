from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from plans.models import IDP
from users.models import Employee


class IsManagerOfEmployee(BasePermission):
    def check_permission(self, user, employee):
        if not hasattr(user, 'manager_profile'):
            return False
        return user.manager_profile.id == employee.head.id

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return self.check_permission(request.user, employee)

    def has_object_permission(self, request, view, obj):
        employee_id = view.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return self.check_permission(request.user, employee)


class IsSelfEmployee(BasePermission):
    def check_permission(self, user, employee):
        if not hasattr(user, 'employee_profile'):
            return False
        return user.employee_profile.id == employee.id

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return self.check_permission(request.user, employee)

    def has_object_permission(self, request, view, obj):
        employee_id = view.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return self.check_permission(request.user, employee)


class IsMentor(BasePermission):

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')
        if not hasattr(request.user, 'employee_profile'):
            return False
        return IDP.objects.filter(
            employee=employee_id,
            mentor=request.user.employee_profile.id
        ).exists()

    def has_object_permission(self, request, view, obj):
        return obj.mentor is not None and obj.mentor.id == request.user.employee_profile.id
