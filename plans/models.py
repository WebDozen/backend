from django.db import models
from users.models import Employee, Manager, User


class ExecutionStatus(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=50,
    )
    slug = models.SlugField(
        verbose_name='Слаг статуса',
        unique=True
    )

    class Meta:
        verbose_name = 'Статус исполнения'
        verbose_name_plural = 'Статусы исполнения'

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
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    description = models.TextField(
        verbose_name='Подробное описание',
    )
    deadline = models.DateTimeField(
        verbose_name='Срок выполнения'
    )
    execution_status = models.ForeignKey(
        ExecutionStatus,
        on_delete=models.CASCADE,
        related_name='IDP',
        verbose_name='Статус исполнения',
        blank=True,
        null=True
    )
    message = models.TextField(
        verbose_name='Мотивационное сообщение',
        blank=True
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'IDP'

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
    execution_status = models.ForeignKey(
        ExecutionStatus,
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
