from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


MAX_LENGTH = 64


class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = 'manager'
        EMPLOYEE = 'employee'

    first_name = models.CharField(max_length=MAX_LENGTH)
    middle_name = models.CharField(max_length=MAX_LENGTH)
    last_name = models.CharField(max_length=MAX_LENGTH)
    role = models.CharField(
        max_length=MAX_LENGTH,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )
    # username = None
    # email = models.EmailField(unique=True)
    # REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name']
    # USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Manager(models.Model):
    """Модель руководителя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='manager_profile'
    )

    class Meta:
        verbose_name = 'Руководитель'
        verbose_name_plural = 'Руководители'


class Employee(models.Model):
    """Модель сотрудника"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    position = models.CharField(max_length=MAX_LENGTH)
    grade = models.CharField(max_length=MAX_LENGTH)
    head = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


class MentorEmployee(models.Model):
    """Модель для связи ментора из числа сотрудников с сотрудником."""
    mentor = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='mentor'
    )
    mentee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='mentee'
    )

    def clean(self):
        if self.mentor == self.mentee:
            raise ValidationError("Сотрудник не может быть своим ментором.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Связь ментор-сотрудник'
        verbose_name_plural = 'Связи ментор-сотрудник'
        constraints = [
            models.UniqueConstraint(
                fields=('mentor', 'mentee'),
                name='unique_mentor_mentee'
            )
        ]
