from django.db import transaction
from rest_framework import serializers
from plans.models import TypeTask, Task, StatusTask


class TypeToTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeTask
        fields = ['id', 'name', 'slug']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusTask
        fields = ['id', 'name', 'slug']


class TaskSerializer(serializers.ModelSerializer):
    type = TypeToTaskSerializer(read_only=True)
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'pub_date', 'name', 'description',
                  'type', 'status']


class TaskCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    type = TypeToTaskSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description',
                  'type']

    def add_type(task, type_data,):
        for type in type_data:
            TypeTask.objects.create(task=task, **type)

    @transaction.atomic
    def create(self, validated_data):
        idps = self.context.get('idpId')
        task = Task.objects.create(idpID=idps, **validated_data)
        return task

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return TaskSerializer(instance).data
"""    def create(self, validate_data):
        idps = self.context.get('idpId')
        type_data = validate_data.pop('type')
        task = Task.objects.create(idpID=idps, **validate_data)
        self.add_type(task, type_data)
        return task"""