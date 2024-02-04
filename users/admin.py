from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Employee, Manager, MentorEmployee, User


@admin.register(MentorEmployee)
class MentorEmployeeAdmin(admin.ModelAdmin):
    pass


class ManagerInline(admin.StackedInline):
    model = Manager
    can_delete = False
    verbose_name_plural = 'Руководитель'


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1
    verbose_name_plural = 'Сотрудник'


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    inlines = (EmployeeInline,)
    list_display = ('id', 'user',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'position', 'grade', 'head')
    search_fields = ('user__email', 'position', 'grade', 'head__user__email')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'last_name',
        'first_name',
        'get_role',
        'position',
        'grade'
    )
    ordering = ('last_name',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'middle_name',
            'last_name'
        )}),
        ('Role', {'fields': ('role',)})
    )

    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': (
            'first_name',
            'middle_name',
            'last_name'
        )}),
        ('Role', {'fields': ('role',)})
    )

    @admin.display(description='Роль')
    def get_role(self, obj):
        if obj.role == 'manager':
            return "Руководитель"
        elif obj.role == 'employee':
            return "Сотрудник"
        return "Пользователь"

    @admin.display(description='Должность')
    def position(self, obj):
        if obj.role == 'employee':
            return obj.employee_profile.position

    @admin.display(description='Грейд')
    def grade(self, obj):
        if obj.role == 'employee':
            return obj.employee_profile.grade

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)

        if obj and obj.role == User.Role.EMPLOYEE:
            inline_instances.append(
                EmployeeInline(self.model, self.admin_site)
            )

        return inline_instances
