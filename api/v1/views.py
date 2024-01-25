from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from plans.models import IDP
from users.models import Employee, Manager
from rest_framework import permissions, status, viewsets
from django.http import HttpResponse
from rest_framework.response import Response
from .serializers import (
    IDPCreateAndUpdateSerializer,
    IDPSerializer,
    IDPDetailSerializer
)


class IDPViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch']

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return IDPCreateAndUpdateSerializer
        elif self.action == 'retrieve':
            return IDPDetailSerializer
        return IDPSerializer

    def perform_create(self, serializer):
        # print('create start')
        manager = Manager.objects.get(user=self.request.user)
        serializer.save(author=manager)
        # print('create compolete')

    def get_queryset(self):
        # print('get_queryset start')
        employee_id = self.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return IDP.objects.filter(employee=employee).prefetch_related('task')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"employee_id": self.kwargs.get('employee_id')})
        return context

    @action(
        detail=True,
        methods=['PATCH']
    )
    def status_change(self, request, employee_id, pk):
        """Подписка."""
        print('status', request, '\n\n\n')
        return Response(
            data='YES', status=status.HTTP_201_CREATED
        )