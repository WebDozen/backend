from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from plans.models import Typetask, Task, StatusTask


class TypeToTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Typetask
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
    status = StatusSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'description',
                  'type', 'status']

    def add_type(task, type_data,):
        for type in type_data:
            Typetask.objects.create(task=task, **type)

    @transaction.atomic
    def create(self, validate_data):
        idpID = self.context.get('idpId')
        type_data = validate_data.pop('type')
        status_data = validate_data.pop('status')
        task = Task.objects.create(idpID=idpID, **validate_data)
        task.status(status_data)
        self.add_type(task, type_data,)
        return task

    @transaction.atomic
    def update(self, instance, validated_data):
        task = instance
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data('description',
                                              instance.description)
        instance.pub_date = validated_data('pub_date', instance.pub_date)
        instance.type.clear()
        instance.status.clear()
        status_data = validated_data.get('status')
        instance.status(status_data)
        type_data = validated_data.get('type')
        Typetask.objects.filter(task=task).delete()
        self.add_type(task, type_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializers = TaskSerializer(instance)
        return serializers.data

