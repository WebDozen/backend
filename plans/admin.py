from django.contrib import admin

from plans.models import (IDP, IdpComment, StatusIDP, StatusTask, Task,
                          TaskComment, TypeTask)


class TaskInlines(admin.StackedInline):
    model = Task
    extra = 1


@admin.register(IDP)
class IDPAdmin(admin.ModelAdmin):
    inlines = [TaskInlines,]
    list_display = ('id', 'name', 'employee', 'status')
    list_filter = ('employee',)
    search_fields = ('employee',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'idp')
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


@admin.register(IdpComment)
class IdpCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'idp')


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task')
