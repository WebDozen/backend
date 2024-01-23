from django.contrib import admin

from plans.models import IDP


@admin.register(IDP)
class IDPAdmin(admin.ModelAdmin):
    pass
