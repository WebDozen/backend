from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from plans.models import Task, IDP, task_comment, idp_comment
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    CommentSerializers,
    TaskCommentSerializer,
    IdpCommentSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskCreateSerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TaskSerializer
        elif self.action in ['create', 'partial_update']:
            return TaskCreateSerializer

    def get_queryset(self):
        idp_id = self.kwargs.get('idpId')
        idp = get_object_or_404(IDP, id=idp_id)
        return Task.objects.filter(idp=idp)

    def perform_create(self, serializer):
        idp = IDP.objects.get()
        serializer.save(author=self.request.user, idp=idp)


class CommentTaskViewsSet(viewsets.ModelViewSet):
    serializer_class = TaskCommentSerializer

    def get_serializer_class(self):
        self.action == 'create'
        return TaskCommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        return task_comment.objects.filter(task=task)

    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        task = get_object_or_404(Task, id=task_id)
        serializer.save(author=self.request.user, task=task)


class CommentIdpViewsSet(viewsets.ModelViewSet):
    serializer_class = IdpCommentSerializer

    def get_serializer_class(self):
        self.action == 'create'
        return IdpCommentSerializer

    def get_queryset(self):
        idp_id = self.kwargs.get('idpId')
        idp = get_object_or_404(IDP, id=idp_id)
        return idp_comment.objects.filter(idp=idp)

    def perform_create(self, serializer):
        idp_id = self.kwargs.get('idpId')
        idp = get_object_or_404(IDP, id=idp_id)
        serializer.save(author=self.request.user, idp=idp)
