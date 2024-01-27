from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes


from users.models import Employee
from plans.models import IDP, Task, StatusIDP


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
        )


class IDPSerializer(serializers.ModelSerializer):
    """Возвращает список объектов всех ИПР конкретного сотрудника"""

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
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

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
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
        # write_only=True
    )

    class Meta:
        model = IDP
        fields = (
            'name',
            'description',
            'deadline',
            'tasks'
        )

    def create_tasks(self, instance, tasks_data):
        """Создает задачи и прикрепляет их к ИПР"""
        for task in tasks_data:
            print(task)
            Task.objects.create(idp=instance, **task)

    def create(self, validated_data):
        tasks_data = validated_data.pop('tasks')
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
        for data in tasks_data:
            task_id = data.get('id')
            task = task_mapping.get(task_id, None)
            if task is None:
                Task.objects.create(idp=instance, **data)
            else:
                for key, value in data.items():
                    setattr(task, key, value)
                task.save()

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
    status = serializers.SerializerMethodField()
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
            'status',
            )

    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)

    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'name': {'type': 'string'},
            'slug': {'type': 'string'},
            'color_fon': {'type': 'string'},
            'color_text': {'type': 'string'},
        }
    })
    def get_status(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            status = idps.last().status
            if status:
                return {
                    'id': status.id,
                    'name': status.name,
                    'slug': status.slug,
                    'color_fon': status.color_fon,
                    'color_text': status.color_text
                }
        return None

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_mentor(self, obj):
        return obj.mentor.exists()
