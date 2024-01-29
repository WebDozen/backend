from django.utils import timezone
from django.db import models
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError

from users.models import Employee, Manager, User


class StatusIDP(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Слаг статуса',
        unique=True
    )
    color_fon = ColorField(verbose_name='Цвет фона')
    color_text = ColorField(verbose_name='Цвет текста')

    class Meta:
        verbose_name = 'Статус исполнения ИПР'
        verbose_name_plural = 'Статусы исполнения ИПР'

    def __str__(self):
        return f'{self.name}'


class IDP(models.Model):
    author = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        null=True,
        related_name='IDP',
        verbose_name='Руководитель',
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='IDP',
        verbose_name='Сотрудник',
    )
    mentor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='IDP_mentor',
        verbose_name='Ментор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name='Подробное описание',
        null=True,
        blank=True,
    )
    deadline = models.DateTimeField(
        verbose_name='Срок выполнения',
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        StatusIDP,
        on_delete=models.CASCADE,
        related_name='IDP',
        verbose_name='Статус исполнения',
        blank=True,
        null=True,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'IDP'

    def __str__(self):
        return f'{self.name}'

    def clean(self):
        if self.employee.head != self.author:
            raise ValidationError(
                'Руководитель не может назначить ИПР работнику, '
                'который не является его сотрудником.'
            )
        if self.mentor and self.mentor.head != self.author:
            raise ValidationError(
                'Руководитель не может назначить ментора, '
                'который не является его сотрудником.'
            )
        if self.mentor == self.employee:
            raise ValidationError('Сотрудник не может быть своим ментором.')
        if self.deadline and self.deadline < timezone.now():
            raise ValidationError(
                'Срок выполнения не может быть меньше текущей даты'
            )

    def save(self, *args, **kwargs):
        self.clean()
        if not self.status:
            default_status_slug = 'open'
            self.status, created = StatusIDP.objects.get_or_create(
                slug=default_status_slug
            )
        super().save(*args, **kwargs)


class StatusTask(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Слаг статуса',
        unique=True
    )
    color_fon = ColorField(verbose_name='Цвет фона')
    color_text = ColorField(verbose_name='Цвет текста')

    class Meta:
        verbose_name = 'Статус исполнения задачи'
        verbose_name_plural = 'Статусы исполнения задачи'

    def __str__(self):
        return f'{self.name}'


class TypeTask(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Слаг типа',
        unique=True
    )

    class Meta:
        verbose_name = 'Тип задач'
        verbose_name_plural = 'Типы задач'

    def __str__(self):
        return f'{self.name}'


class Task(models.Model):
    idp = models.ForeignKey(
        IDP,
        on_delete=models.CASCADE,
        related_name='task',
        verbose_name='ИПР',
    )
    type = models.ForeignKey(
        TypeTask,
        on_delete=models.CASCADE,
        related_name='task',
        verbose_name='Тип задачи',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    description = models.TextField(
        verbose_name='Подробное описание',
    )
    source = models.CharField(
        verbose_name='Источник',
        max_length=200,
    )
    status = models.ForeignKey(
        StatusTask,
        on_delete=models.CASCADE,
        related_name='task',
        verbose_name='Статус исполнения',
        blank=True,
        null=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        if not self.status:
            default_status_slug = 'open'
            self.status, created = StatusTask.objects.get_or_create(
                slug=default_status_slug
            )
        super().save(*args, **kwargs)


class Comments(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_author',
        verbose_name='Пользователь',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class IdpComment(Comments):
    idp = models.ForeignKey(
        IDP,
        on_delete=models.CASCADE,
        related_name='idp_comments',
        verbose_name='ИПР',
    )

    class Meta:
        verbose_name = 'Комментарий к ИПР'
        verbose_name_plural = 'Комментарии к ИПР'

    def __str__(self):
        return f'{self.text}'


class TaskComment(Comments):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_comments',
        verbose_name='Задача',
    )

    class Meta:
        verbose_name = 'Комментарий к задаче'
        verbose_name_plural = 'Комментарии к задаче'

    def __str__(self):
        return f'{self.text}'
