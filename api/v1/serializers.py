from django.shortcuts import get_object_or_404
from django.db.models import Max
from django.contrib.auth import get_user_model
from django.db.models import Max
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plans.models import (IDP, IdpComment, StatusIDP, StatusTask, Task,
                          TaskComment)
from users.models import Employee, Manager

User = get_user_model()


class EmployeeOrMentorSerializer(serializers.ModelSerializer):
    """Возвращает объект Employee"""

    last_name = serializers.ReadOnlyField(source='user.last_name')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    middle_name = serializers.ReadOnlyField(source='user.middle_name')

    class Meta:
        model = Employee
        fields = (
            'id',
            'last_name',
            'first_name',
            'middle_name',
            'grade',
            'position'
        )


class StatusIDPSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели StatusIDP"""

    class Meta:
        model = StatusIDP
        fields = '__all__'


class StatusTaskSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели StatusTask"""

    class Meta:
        model = StatusTask
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Task"""

    status = StatusTaskSerializer()

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'description',
            'type',
            'source',
            'status'
        )


class TaskCreateSerializer(serializers.ModelSerializer):
    """Обрабатывает POST-запросы к модели Task"""

    id = serializers.IntegerField(required=False)

    class Meta:
        model = Task
        fields = (
            'id',
            'type',
            'name',
            'description',
            'source'
        )


class IDPSerializer(serializers.ModelSerializer):
    """Возвращает список объектов всех ИПР конкретного сотрудника"""

    status = StatusIDPSerializer()
    mentor = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
            'name',
            'deadline',
            'mentor',
            'tasks',
            'status',
        )

    def get_mentor(self, obj) -> bool:
        """Проверка есть ли ментор у ИПР"""
        return obj.mentor is not None

    def get_tasks(self, obj) -> bool:
        """Проверка есть ли задачи у ИПР"""
        return obj.task.exists()


class IDPDetailSerializer(serializers.ModelSerializer):
    """Возвращает объект конкретного ИПР конкретного сотрудника"""

    tasks = TaskSerializer(
        many=True,
        source='task',
        read_only=True
    )
    status = StatusIDPSerializer()
    mentor = EmployeeOrMentorSerializer()
    statistic = serializers.SerializerMethodField()

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
            'mentor',
            'name',
            'description',
            'pub_date',
            'deadline',
            'status',
            'tasks',
            'statistic'
        )

    @extend_schema_field({
        'properties': {
            'count_task': {'type': 'integer'},
            'task_done': {'type': 'integer'}
        }
    })
    def get_statistic(self, obj) -> dict:
        """Возвращает кол-во задач и кол-во завершенных задач ИПР"""
        count_task = obj.task.count()
        task_done = obj.task.filter(status__slug='completed').count()
        return {'count_task': count_task, 'task_done': task_done}


class IDPCreateAndUpdateSerializer(serializers.ModelSerializer):
    """Обрабатывает POST и PATCH запросы объекта IPD"""

    tasks = TaskCreateSerializer(
        many=True,
        required=False
        # write_only=True
    )

    class Meta:
        model = IDP
        fields = (
            'mentor',
            'name',
            'description',
            'deadline',
            'tasks'
        )

    def validate(self, data):
        if self.partial:
            return data

        author_manager = self.context['request'].user.id
        employee_id = self.context.get('employee_id')
        mentor = data.get('mentor', None)
        tasks_data = data.get('tasks', [])
        last_idp = IDP.objects.filter(
            employee=employee_id
        ).order_by('-pub_date').first()

        if (
            last_idp and
            last_idp.status.slug in ['open', 'in_progress', 'awaiting_review']
        ):
            raise serializers.ValidationError(
                {'status': 'Сотрудник не может иметь несколько активных ИПР'}
            )

        if mentor is not None:
            if mentor.head.id != author_manager:
                raise serializers.ValidationError(
                    {'mentor': [
                        'Руководитель не может назначить ментором сотрудника, '
                        'который не является его сотрудником.'
                    ]}
                )

            if mentor.id == int(employee_id):
                raise serializers.ValidationError(
                    {'mentor': [
                        'Сотрудник не может быть своим ментором.'
                    ]}
                )
            if not data.get('name'):
                raise serializers.ValidationError(
                    {'name': 'Укажите название ИПР'}
                )
            return data

        required_fields = ['name', 'description', 'deadline']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f'{field} обязательно.'}
                )
        if data.get('deadline') < timezone.now():
            raise serializers.ValidationError(
                {'deadline': (
                    'Срок выполнения не может быть меньше текущей даты'
                )}
            )
        if not tasks_data:
            raise serializers.ValidationError(
                {'tasks': 'Необходимо добавить хотя бы одну задачу'}
            )

        return data

    def validate_task_on_upgrade(self, task_data):
        """Валидирует данные созданных задач при редактировании ИПР"""
        if not all(task_data.get(field) for field
                   in ['name', 'description', 'source', 'type']):
            raise serializers.ValidationError(
                {'tasks': (
                    'Все поля (name, description, source, type)'
                    'обязательны для создания новой задачи.'
                )}
            )

    def create_tasks(self, instance, tasks_data):
        """Создает задачи и прикрепляет их к ИПР"""
        for task in tasks_data:
            Task.objects.create(idp=instance, **task)

    def create(self, validated_data):
        tasks_data = validated_data.pop('tasks', [])
        employee_id = self.context.get('employee_id')
        instance = IDP.objects.create(
            employee_id=employee_id,
            **validated_data
        )
        self.create_tasks(instance, tasks_data)
        return instance

    def upgrade_tasks(self, instance, tasks_data):
        """Создает новые или обновляет существующие задачи ИПР"""
        task_mapping = {task.id: task for task in instance.task.all()}
        for task_data in tasks_data:
            task_id = task_data.get('id')
            task = task_mapping.get(task_id, None)

            if task is not None:
                for key, value in task_data.items():
                    setattr(task, key, value)
                task.save()
            elif task_id is not None:
                raise serializers.ValidationError(
                    {'tasks': f'Задачи с id {task_id} нет у ИПР'}
                )
            else:
                self.validate_task_on_upgrade(task_data)
                Task.objects.create(idp=instance, **task_data)

        for task_id, task in task_mapping.items():
            if task_id not in [data.get('id') for data in tasks_data]:
                task.delete()

    def update(self, instance, validated_data):
        tasks_data = validated_data.pop('tasks', [])
        instance = super().update(instance, validated_data)
        self.upgrade_tasks(instance, tasks_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return IDPDetailSerializer(instance).data


class IDPStatusUpdateSerializer(serializers.ModelSerializer):
    """Обрабатывает PATCH запрос на обновление статуса ИПР"""

    class Meta:
        model = IDP
        fields = ['status']

    status = serializers.SlugRelatedField(
        queryset=StatusIDP.objects.all(),
        slug_field='slug',
    )

    def validate_status(self, value):
        current_idp = self.instance
        employee = current_idp.employee
        latest_idp_pub_date = IDP.objects.filter(
            employee=employee
        ).aggregate(latest_idp=Max('pub_date'))['latest_idp']
        allowed_slugs = ['cancelled', 'completed']
        if current_idp.pub_date != latest_idp_pub_date:
            raise serializers.ValidationError(
                'Нельзя менять статус старых ИПР'
            )
        if value.slug not in allowed_slugs:
            raise serializers.ValidationError('Неверный slug статуса')
        if (
            value.slug == 'cancelled' and
            current_idp.status.slug in ['completed', 'expired']
        ):
            raise serializers.ValidationError(
                'Нельзя отменить завершенный или просроченный ИПР'
            )
        if (
            value.slug == 'completed' and
            current_idp.status.slug != 'awaiting_review'
        ):
            raise serializers.ValidationError(
                'Нельзя завершить ИПР без ревью'
            )
        return value

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        return instance

    def to_representation(self, instance):
        return StatusIDPSerializer(instance.status).data


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников."""

    idp = serializers.SerializerMethodField()
    mentor = serializers.SerializerMethodField()
    is_mentor = serializers.SerializerMethodField()
    last_name = serializers.ReadOnlyField(source='user.last_name')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    middle_name = serializers.ReadOnlyField(source='user.middle_name')

    class Meta:
        model = Employee
        fields = (
            'id',
            'mentor',
            'last_name',
            'first_name',
            'middle_name',
            'grade',
            'position',
            'is_mentor',
            'idp',
        )

    def __init__(self, *args, **kwargs):
        self.exclude_mentor_and_status = kwargs.pop(
            'exclude_mentor_and_status',
            False)
        super().__init__(*args, **kwargs)

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'status': {'type': 'string'},
            'has_task': {'type': 'boolean'},
            'completed_tasks_count': {'type': 'integer'},
            'total_completed_idps': {'type': 'integer'},
            'total_tasks_count': {'type': 'integer'},
            'total_idp_count': {'type': 'integer'},
        }
    })
    def get_idp(self, obj):
        idps = obj.IDP.all()
        latest_idp = idps.last() if idps.exists() else None
        total_idp_count = idps.count()
        if latest_idp:
            completed_tasks_count = latest_idp.task.filter(
                status__slug='completed').count()
            total_completed_idps = idps.filter(
                status__slug='completed').count()
            total_tasks_count = latest_idp.task.count()
            return {
                'status':
                latest_idp.status.slug if latest_idp.status else 'none',
                'has_task': latest_idp.task.exists() if latest_idp else False,
                'completed_tasks_count': completed_tasks_count,
                'total_completed_idps': total_completed_idps,
                'total_tasks_count': total_tasks_count,
                'total_idp_count': total_idp_count,
            }
        return {
            'status': 'none',
            'has_task': False,
            'completed_tasks_count': 0,
            'total_completed_idps': 0,
            'total_tasks_count': 0,
            'total_idp_count': 0,
        }

    def get_mentor(self, obj) -> bool:
        latest_idp = obj.IDP.last()
        if latest_idp:
            return bool(latest_idp.mentor)
        return False

    def get_is_mentor(self, obj) -> bool:
        return obj.IDP_mentor.exists()


class HeadStatisticSerializer(serializers.ModelSerializer):
    """Возвращает статистику по руководителю"""

    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Manager
        fields = ('statistics',)

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'count_employe': {'type': 'integer'},
            'count_employe_with_idp': {'type': 'integer'},
            'percent_progress_employees': {'type': 'integer'},
            'count_employe_without_idp': {'type': 'integer'},
            'count_idp_without_tasks': {'type': 'integer'},
            'count_idp_with_status_not_done': {'type': 'integer'},
            'count_idp_with_status_awaiting_review': {'type': 'integer'},
        }
    })
    def get_statistics(self, obj):
        """Сериализатор статистики"""
        employees = Employee.objects.filter(
            head=obj.id
        ).prefetch_related('IDP')
        idps = IDP.objects.filter(
            author=obj.id, employee__in=employees
        ).prefetch_related('task')
        tasks = Task.objects.filter(idp__in=idps)
        current_idps = []

        count_employe_with_idp = 0
        count_idp_with_status_not_done = 0
        count_idp_with_status_cancelled = 0
        count_idp_status_review = 0
        active_statuses = ['in_progress', 'open', 'awaiting_review']
        for employee in employees:
            idp = idps.filter(employee=employee).last()
            if idp:
                if idp.status.slug in active_statuses:
                    count_employe_with_idp += 1
                elif idp.status.slug == 'expired':
                    count_idp_with_status_not_done += 1
                elif idp.status.slug == 'cancelled':
                    count_idp_with_status_cancelled += 1
                if idp.status.slug == 'awaiting_review':
                    count_idp_status_review += 1
                current_idps.append(idp)
        count_employe = employees.count()

        idps_with_tasks = idps.filter(task__in=tasks)
        count_idp_without_tasks = (
            len(current_idps) - len(
                set(current_idps).intersection(list(idps_with_tasks))
            )
        )

        if count_employe:
            percent_progress_employees = int(
                100 * count_employe_with_idp / count_employe
            )
        else:
            percent_progress_employees = None
        count_employe_without_idp = (
            count_employe - count_employe_with_idp
        )
        data = {
            'count_employe': count_employe,
            'count_employe_with_idp': count_employe_with_idp,
            'percent_progress_employees': percent_progress_employees,
            'count_employe_without_idp': count_employe_without_idp,
            'count_idp_without_tasks': count_idp_without_tasks,
            'count_idp_with_status_not_done': count_idp_with_status_not_done,
            'count_idp_with_status_awaiting_review': count_idp_status_review,
            'count_idp_with_status_cancelled': count_idp_with_status_cancelled
        }
        return data


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """Обрабатывает PATCH запрос на обновление статуса задачи ИПР"""
    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, attrs):
        idp_id = self.instance.idp.id
        idp = get_object_or_404(IDP, id=idp_id)
        if idp.status.slug in ['completed', 'expired', 'cancelled']:
            raise serializers.ValidationError(
                'Нельзя менять статус задач завершенных, '
                'отмененных или просроченных ИПР'
            )
        employee = idp.employee
        latest_idp_pub_date = IDP.objects.filter(
            employee=employee
        ).aggregate(latest_idp=Max('pub_date'))['latest_idp']
        if idp.pub_date != latest_idp_pub_date:
            raise serializers.ValidationError(
                'Нельзя менять статус задач старого ИПР'
            )
        return super().validate(attrs)

    def to_representation(self, instance):
        return StatusTaskSerializer(instance.status).data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""

    last_name = serializers.ReadOnlyField(source='user.last_name')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    middle_name = serializers.ReadOnlyField(source='user.middle_name')

    class Meta:
        model = User
        fields = (
            'id',
            'last_name',
            'first_name',
            'middle_name'
        )


class IDPCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к ИПР"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = IdpComment
        fields = ('id', 'text', 'pub_date', 'author')

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'middle_name': {'type': 'string'},
            'is_mentor': {'type': 'boolean'}
        }
    })
    def get_author(self, obj):
        user = obj.author
        idp = self.context.get('idp')
        author_data = {}
        if user.role == 'manager':
            author_data.update(UserSerializer(user.manager_profile).data)
            author_data['is_mentor'] = False
        elif user.role == 'employee':
            author_data.update(UserSerializer(user.employee_profile).data)
            author_data['is_mentor'] = idp.mentor == user.employee_profile
        return author_data


class TaskCommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев к задаче"""
    author = serializers.SerializerMethodField()

    class Meta:
        model = TaskComment
        fields = ('id', 'text', 'pub_date', 'author')

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'middle_name': {'type': 'string'},
            'is_mentor': {'type': 'boolean'}
        }
    })
    def get_author(self, obj):
        user = obj.author
        idp = self.context.get('idp')
        author_data = {}
        if user.role == 'manager':
            author_data.update(UserSerializer(user.manager_profile).data)
            author_data['is_mentor'] = False
        elif user.role == 'employee':
            author_data.update(UserSerializer(user.employee_profile).data)
            author_data['is_mentor'] = idp.mentor == user.employee_profile
        return author_data
