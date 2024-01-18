from django.contrib import admin

from users.models import Manager, Employee


class EmloyeeInline(admin.TabularInline):
    model = Employee
    extra = 1


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = '__all__'
    inlines = (EmloyeeInline)
