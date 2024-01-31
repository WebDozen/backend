from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from plans.models import TypeTask, Task, StatusTask, task_comment, idp_comment


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
        idp_id = self.context.get('idpId')
        task = Task.objects.create(idp_id=idp_id, **validated_data)
        return task

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return TaskSerializer(instance).data


class CommentSerializers(serializers.Serializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
        )

    class Meta:
        fields = ['id', 'pub_date', 'author', 'text']


class TaskCommentSerializer(CommentSerializers, serializers.ModelSerializer):

    class Meta:
        model = task_comment
        fields = CommentSerializers.Meta.fields + ['task_id']


class IdpCommentSerializer(CommentSerializers, serializers.ModelSerializer):

    class Meta:
        model = idp_comment
        fields = CommentSerializers.Meta.fields + ['idpID']
