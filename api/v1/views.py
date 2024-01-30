from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from plans.models import Task, IDP
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
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
