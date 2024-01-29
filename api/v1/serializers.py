from django.utils import timezone
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes


from users.models import Employee
from plans.models import IDP, Task, StatusIDP


class MentorSerializer(serializers.ModelSerializer):

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
    """Возвращает объекты модели ExecutionStatus"""

    class Meta:
        model = StatusIDP
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Task"""

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'description',
            'type',
            'source',
            'status',
            'pub_date'
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
    mentor = MentorSerializer()

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
            'mentor',
            'name',
            'deadline',
            'status',
        )


class IDPDetailSerializer(serializers.ModelSerializer):
    """Возвращает объект конкретного ИПР конкретного сотрудника"""

    tasks = TaskSerializer(
        many=True,
        source='task',
        read_only=True
    )
    status = StatusIDPSerializer()
    mentor = MentorSerializer()

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
            'tasks'
        )


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
        author_manager = self.context['request'].user.id
        employee_id = self.context.get('employee_id')
        mentor = data.get('mentor', None)
        tasks_data = data.get('tasks', [])

        if self.partial:
            return data

        if mentor is not None:
            if mentor.head.id != author_manager:
                raise serializers.ValidationError(
                    {'mentor': [
                        'Руководитель не может назначить ментора, '
                        'который не является его сотрудником.'
                    ]}
                )

            if mentor.id == int(employee_id):
                raise serializers.ValidationError(
                    {'mentor': [
                        'Сотрудник не может быть своим ментором.'
                    ]}
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
            print(task)
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


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников."""

    idp = serializers.SerializerMethodField()
    mentor = serializers.SerializerMethodField()
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
            'total_completed_idps': {'type': 'integer'},
            'completed_tasks_count': {'type': 'integer'},
            'total_idps_count': {'type': 'integer'},
        }
    })
    def get_idp(self, obj):
        idps = obj.IDP.all()
        total_idps_count = idps.count()
        latest_idp = idps.last() if idps.exists() else None
        if latest_idp:
            completed_tasks_count = latest_idp.task.filter(
                status__slug='completed').count()
            total_completed_idps = idps.filter(
                status__slug='completed').count()
            return {
                'status': latest_idp.status.slug if latest_idp.status else 'none',
                'has_task': latest_idp.task.exists() if latest_idp else False,
                'total_completed_idps': total_completed_idps,
                'completed_tasks_count': completed_tasks_count,
                'total_idps_count': total_idps_count,
            }
        return {
            'status': 'none',
            'has_task': False,
            'total_completed_idps': 0,
            'completed_tasks_count': 0,
            'total_idps_count': total_idps_count,
        }

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_mentor(self, obj):
        return obj.mentor.exists()
