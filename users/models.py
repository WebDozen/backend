from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


MAX_LENGHT = 64


class User(AbstractUser):

    class Role(models.TextChoices):
        MANAGER = 'manager'
        EMPLOYEE = 'employee'

    first_name = models.CharField(max_lenght=MAX_LENGHT)
    middle_name = models.CharField(max_lenght=MAX_LENGHT)
    last_name = models.CharField(max_lenght=MAX_LENGHT)
    role = models.CharField(
        max_lenght=MAX_LENGHT,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_plural_name = 'Пользователи'


class Manager(models.Model):
    """Модель руководителя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Руководитель'
        verbose_plural_name = 'Руководители'


class Employee(models.Model):
    """Модель сотрудника"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_lenght=MAX_LENGHT)
    grade = models.CharField(max_lenght=MAX_LENGHT)
    head = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_plural_name = 'Сотрудники'


class MentorEmployee(models.Model):
    """Модель для связи ментора из числа сотрудников с сотрудником."""
    mentor = models.ForeignKey(Employee, on_delete=models.CASCADE)
    mentee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def clean(self):
        if self.mentor == self.mentee.supervisor:
            raise ValidationError("Сотрудник не может быть своим ментором.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Связь ментор-сотрудник'
        verbose_plural_name = 'Связи ментор-сотрудник'
        constraints = [
            models.UniqueConstraint(
                fields=('mentor', 'mentee'),
                name='unique_mentor_mentee'
            )
        ]
