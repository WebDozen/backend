from rest_framework.permissions import BasePermission

from users.models import Employee
from plans.models import IDP


class IsManagerIDP(BasePermission):
    """Является ли пользователь руководителем сотрудника ИПР"""

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')

        if request.user.role == 'manager':
            try:
                employee = Employee.objects.get(id=employee_id)
                return request.user.manager_profile.id == employee.head.id
            except Employee.DoesNotExist:
                return False

        return False


class IsEmployeeIDP(BasePermission):
    """Является ли пользователь сотрудником у ИПР"""

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')

        if request.user.role == 'employee':
            return request.user.employee_profile.id == int(employee_id)


class IsMentorIDP(BasePermission):
    """Является ли пользователь ментором сотрудника у ИПР"""

    def has_permission(self, request, view):
        employee_id = view.kwargs.get('employee_id')
        idp_pk = view.kwargs.get('pk') if 'pk' in view.kwargs else None

        if request.user.role == 'employee':
            if idp_pk:
                try:
                    print('try')
                    employee = Employee.objects.get(id=employee_id)
                    idp = IDP.objects.get(
                        id=idp_pk,
                        employee=employee,
                        mentor=request.user.employee_profile.id
                    )
                    print(idp)
                    return True
                except IDP.DoesNotExist:
                    return False
            return IDP.objects.filter(
                employee=employee_id,
                mentor=request.user.employee_profile.id
            ).exists()

        return False


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
