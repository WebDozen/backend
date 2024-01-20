from django.contrib import admin

from users.models import Manager, Employee, User


class EmloyeeInline(admin.TabularInline):
    model = Employee
    extra = 1


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    inlines = (EmloyeeInline,)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
