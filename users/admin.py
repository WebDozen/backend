from django.contrib import admin

from users.models import Manager, Employee, User, MentorEmployee


@admin.register(MentorEmployee)
class MentorEmployeeAdmin(admin.ModelAdmin):
    pass


# class EmloyeeInline(admin.TabularInline):
#     model = Employee
#     extra = 1


# @admin.register(Manager)
# class ManagerAdmin(admin.ModelAdmin):
#     inlines = (EmloyeeInline,)


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     pass


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
    list_display = ('user',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'grade', 'head')
    search_fields = ('user__email', 'position', 'grade', 'head__user__email')


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'get_role')
    ordering = ('email',)

    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)

        if obj and obj.role == User.Role.EMPLOYEE:
            inline_instances.append(
                EmployeeInline(self.model, self.admin_site)
            )

        return inline_instances

    @admin.display(description='Роль')
    def get_role(self, obj):
        if obj.role == 'manager':
            return "Руководитель"
        elif obj.role == 'employee':
            return "Сотрудник"
        return "Пользователь"

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'first_name',
            'middle_name',
            'last_name'
        )}),
        ('Role', {'fields': ('role',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'role'),
        }),
    )
