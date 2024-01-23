# Generated by Django 3.2 on 2024-01-23 12:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Execution_status',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг статуса')),
            ],
            options={
                'verbose_name': 'Статус исполнения',
                'verbose_name_plural': 'Статусы исполнения',
            },
        ),
        migrations.CreateModel(
            name='IDP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Подробное описание')),
                ('deadline', models.DateTimeField(verbose_name='Дедлайн')),
                ('message', models.TextField(verbose_name='Мотивационное сообщение')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='IDP', to='users.manager', verbose_name='Руководитель')),
                ('employee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='IDP', to='users.employee', verbose_name='Сотрудник')),
                ('execution_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='IDP', to='plans.execution_status', verbose_name='Статус исполнения')),
            ],
            options={
                'verbose_name': 'IDP',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Подробное описание')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('execution_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='plans.execution_status', verbose_name='Статус исполнения')),
                ('idp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='plans.idp', verbose_name='ИПР')),
            ],
            options={
                'verbose_name': 'Задача',
                'verbose_name_plural': 'Задачи',
            },
        ),
        migrations.CreateModel(
            name='Type_task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('slug', models.SlugField(unique=True, verbose_name='Слаг типа')),
            ],
            options={
                'verbose_name': 'Тип задачи',
                'verbose_name_plural': 'Типы задачи',
            },
        ),
        migrations.CreateModel(
            name='task_comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_comment_author', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_comments', to='plans.task', verbose_name='Задача')),
            ],
            options={
                'verbose_name': 'Комментарий к задаче',
                'verbose_name_plural': 'Комментарии к задаче',
            },
        ),
        migrations.AddField(
            model_name='task',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task', to='plans.type_task', verbose_name='Тип задачи'),
        ),
        migrations.CreateModel(
            name='idp_comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст комментария')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата комментария')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idp_comment_author', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('idp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='idp_comments', to='plans.idp', verbose_name='ИПР')),
            ],
            options={
                'verbose_name': 'Комментарий к ИПР',
                'verbose_name_plural': 'Комментарии к ИПР',
            },
        ),
    ]