from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from users.models import Employee
from plans.models import IDP


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
        return (
            obj.mentor is not None and
            obj.mentor.id == request.user.employee_profile.id
        )


class IsManagerandEmployee(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if hasattr(request.user, 'manager_profile'):
                return True
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'manager_profile'):
            return True
        if hasattr(request.user, 'employee_profile'):
            mentor_idp = IDP.objects.filter(
                mentor=request.user.employee_profile,
                employee=obj)
            if mentor_idp.exists():
                return True
            return obj == request.user.employee_profile
        return False


class IsEmployeeIDPExecutor(BasePermission):
    def check_permission(self, user, employee):
        if not hasattr(user, 'employee_profile'):
            return False
        return user.employee_profile.id == employee.id

    def has_permission(self, request, view):
        idp_id = view.kwargs.get('idp_id')
        idp = get_object_or_404(IDP, id=idp_id)
        employee = idp.employee
        return self.check_permission(request.user, employee)
