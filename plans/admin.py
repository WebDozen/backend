from django.contrib import admin

from plans.models import IDP, StatusIDP, Task, TypeTask, StatusTask


class TaskInlines(admin.StackedInline):
    model = Task
    extra = 1


@admin.register(IDP)
class IDPAdmin(admin.ModelAdmin):
    inlines = [TaskInlines,]
    list_display = ('id', 'name')
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    pass


@admin.register(TypeTask)
class TypeTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(StatusIDP)
class StatusIDPAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


@admin.register(StatusTask)
class StatusTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
