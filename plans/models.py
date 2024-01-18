from django.db import models
from users.models import Employee, Manager


class Execution_status(models.Model):
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


class IPR(models.Model):
    author = models.ForeignKey(
        Manager,
        on_delete=models.SET_NULL,
        null=True,
        related_name='IPR',
        verbose_name='Руководитель',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    description = models.TextField(
        verbose_name='Подробное описание',
    )
    deadline = models.DateTimeField(
        verbose_name='Дедлайн'
    )
    execution_status = models.ManyToManyField(
        Execution_status,
        verbose_name='Статус исполнения',
        related_name='IPR',
    )

    class Meta:
        verbose_name = 'IPR'

    def __str__(self):
        return f'{self.name}'


class manager_comment(models.Model):
    ipr = models.ForeignKey(
        IPR,
        on_delete=models.CASCADE,
        related_name='manager comments',
        verbose_name='ИПР',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        Manager,
        on_delete=models.CASCADE,
        related_name='manager comments',
        verbose_name='Руководитель',
    )
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий Руководителя'
        verbose_name_plural = 'Комментарии Руководителя'

    def __str__(self):
        return f'{self.text}'


class employee_comment(models.Model):
    ipr = models.ForeignKey(
        IPR,
        on_delete=models.CASCADE,
        related_name='employee comments',
        verbose_name='ИПР',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='employee comments',
        verbose_name='Сотрудник',
    )
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий Сотрудника'
        verbose_name_plural = 'Комментарии Сотрудника'

    def __str__(self):
        return f'{self.text}'
