from rest_framework import serializers

from plans.models import IDP, Task, ExecutionStatus
from users.models import User, Manager, MentorEmployee, Employee



class TaskSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Task"""

    class Meta:
        model = Task
        fields = (
            'id',
            'name',
            'description',
            'type',
            'execution_status',
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
            'execution_status',
        )


class IDPDetailSerializer(serializers.ModelSerializer):
    """Возвращает объект конкретного ИПР конкретного сотрудника"""

    tasks = TaskSerializer(
        many=True,
        source='task',
        read_only=True
    )

    class Meta:
        model = IDP
        fields = (
            'id',
            'employee',
            'name',
            'description',
            'pub_date',
            'deadline',
            'execution_status',
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



class HeadStatisticSerializer(serializers.ModelSerializer):
    """Возвращает объекты модели Task"""
    count_employe = serializers.SerializerMethodField()
    count_employe_with_idp = serializers.SerializerMethodField()
    percent_progress_employees = serializers.SerializerMethodField()
    count_employe_without_idp = serializers.SerializerMethodField()
    count_idp_without_tasks = serializers.SerializerMethodField()
    count_idp_with_status_not_done = serializers.SerializerMethodField()
    count_idp_with_status_awaiting_review = serializers.SerializerMethodField()

    class Meta:
        model = Manager

        fields = (
            'count_employe',
            'count_employe_with_idp',
            'percent_progress_employees',
            'count_employe_without_idp',
            'count_idp_without_tasks',
            'count_idp_with_status_not_done',
            'count_idp_with_status_awaiting_review',
        )
    
    def get_count_employe(self, obj):
        count_employe = MentorEmployee.objects.filter(mentor=obj.id).count()
        return count_employe
    
    def get_count_employe_with_idp(self, obj):
        count_employe_with_idp = Employee.objects.filter(
            head=obj.id, IDP__isnull=False
        ) | Employee.objects.filter(
            mentor=obj.id,
            IDP__isnull=False
        )
        return len(count_employe_with_idp)
    
    def get_percent_progress_employees(self, obj):
        progress = (
            100 * self.get_count_employe_with_idp(obj) /
            self.get_count_employe(obj)
        )
        return int(progress)

    def get_count_employe_without_idp(self, obj):
        count_employe_without_idp = (
            self.get_count_employe(obj) -
            self.get_count_employe_with_idp(obj)
        )
        return count_employe_without_idp
    
    def get_count_idp_without_tasks(self, obj):
        idp_without_tasks = IDP.objects.filter(
            author=obj.id, task=None
        ).count()
        return idp_without_tasks
    
    def get_count_idp_with_status_not_done(self, obj):
        status = ExecutionStatus.objects.get(slug='not_done')
        idp_not_done = IDP.objects.filter(
            author=obj.id,
            execution_status=status
        )
        return len(idp_not_done)
    
    def get_count_idp_with_status_awaiting_review(self, obj):
        status = ExecutionStatus.objects.get(slug='awaiting_review')
        idp_awaiting_review = IDP.objects.filter(
            author=obj.id,
            execution_status=status
        )
        return len(idp_awaiting_review)

class EmployeeSerializer(serializers.ModelSerializer):
    idp_status = serializers.SerializerMethodField()
    mentor_id = serializers.SerializerMethodField()
    idp_id = serializers.SerializerMethodField()
    last_name = serializers.ReadOnlyField(source='user.last_name')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    middle_name = serializers.ReadOnlyField(source='user.middle_name')
    message = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id',
                  'head',
                  'mentor_id',
                  'idp_id',
                  'last_name',
                  'first_name',
                  'middle_name',
                  'grade',
                  'position',
                  'task_count',
                  'idp_status',
                  'message',
                  ]

    def __init__(self, *args, **kwargs):
        self.manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)

    def get_task_count(self, obj):
        if self.manager and obj.head == self.manager:
            tasks = Task.objects.filter(idp__employee=obj)
            return tasks.count()
        return 0

    def get_idp_status(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().execution_status.name
        else:
            return None

    def get_mentor_id(self, obj):
        return obj.mentor.exists()

    def get_idp_id(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().id
        else:
            return None

    def get_message(self, obj):
        idps = obj.IDP.all()
        if idps.exists():
            return idps.first().message
        else:
            return None

