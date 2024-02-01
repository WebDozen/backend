# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from .models import User, Manager, Employee


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if instance.role == User.Role.MANAGER:
#         Manager.objects.get_or_create(user=instance)
#     elif instance.role == User.Role.EMPLOYEE:
#         Employee.objects.get_or_create(user=instance)


# @receiver(pre_save, sender=User)
# def update_user_profile(sender, instance, **kwargs):
#     try:
#         original_user = User.objects.get(pk=instance.pk)
#     except User.DoesNotExist:
#         return

#     if instance.role != original_user.role:
#         # Роль пользователя была изменена
#         if instance.role == User.Role.MANAGER:
#             Employee.objects.filter(user=instance).delete()
#             Manager.objects.get_or_create(user=instance)
#         elif instance.role == User.Role.EMPLOYEE:
#             Manager.objects.filter(user=instance).delete()
#             Employee.objects.create(user=instance)
