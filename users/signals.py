from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee, Manager, User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if instance.role == User.Role.MANAGER:
        Manager.objects.get_or_create(user=instance)
    elif instance.role == User.Role.EMPLOYEE:
        Employee.objects.get_or_create(user=instance)
