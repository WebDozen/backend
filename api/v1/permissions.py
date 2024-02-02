from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from users.models import Employee
from plans.models import IDP, Task


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
                    employee = Employee.objects.get(id=employee_id)
                    IDP.objects.get(
                        id=idp_pk,
                        employee=employee,
                        mentor=request.user.employee_profile.id
                    )
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


class IsEmployeeIDPExecutor(IsEmployeeIDP):
    """Является ли пользователь исполнителем ИПР"""

    def check_permission(self, user, employee):
        if not hasattr(user, 'employee_profile'):
            return False
        return user.employee_profile.id == employee.id

    def has_permission(self, request, view):
        idp_id = view.kwargs.get('idp_id')
        idp = get_object_or_404(IDP, id=idp_id)
        employee = idp.employee
        return self.check_permission(request.user, employee)


class Comments(BasePermission):
    """
    Разрешение для управления комментариями к ИПР и задачам
    в зависмости от роли пользователя
    """

    def has_permission(self, request, view):
        idp_id = view.kwargs.get('idp_id', None)
        task_id = view.kwargs.get('task_id', None)
        current_user = request.user

        def is_manager_author(idp):
            """Является ли пользователь руководителем сотрудника"""
            return idp.employee.head == current_user.manager_profile

        def is_employee_or_mentor(idp):
            """Связан ли пользователь с ИПР как сотрудник или ментор"""
            return (
                idp.employee == current_user.employee_profile or
                idp.mentor == current_user.employee_profile
            )

        def get_idp():
            """Получает объет ИПР"""
            if idp_id:
                return IDP.objects.get(id=idp_id)
            elif task_id:
                task = Task.objects.get(id=task_id)
                return task.idp

        try:
            idp = get_idp()
            if current_user.role == 'manager':
                return is_manager_author(idp)
            elif current_user.role == 'employee':
                return is_employee_or_mentor(idp)
        except (IDP.DoesNotExist, Task.DoesNotExist):
            return False

        return False
