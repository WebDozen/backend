from backend.plans import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    class Role(models.TextChoices):
        HEAD = "head"
        EMPLOYEE = "employee"

    middle_name = models.CharField(max_length=50)

    role = models.CharField(
        "Роль",
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=50, blank=True, null=True)
    grade = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Профиль сотрудника'
        verbose_name_plural = 'Профили сотрудников'


# class HeadProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = 'Профиль руководителя'
#         verbose_name_plural = 'Профили руководителей'
