from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, views, permissions
from rest_framework import generics

from users.models import Employee, Manager, User
from plans.models import IDP
from .serializers import (
    IDPCreateAndUpdateSerializer,
    IDPSerializer,
    IDPDetailSerializer,
    EmployeeSerializer,
    HeadStatisticSerializer,
    EmployeeStatisticSerializer
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
        manager = Manager.objects.get(user=self.request.user)
        serializer.save(author=manager)

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return IDP.objects.filter(employee=employee).prefetch_related('task')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"employee_id": self.kwargs.get('employee_id')})
        return context


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            manager = self.request.user.manager_profile
            context.update({'manager': manager})
        except Manager.DoesNotExist:
            context.update({'manager': None})
        return context

    def list(self, request, *args, **kwargs):
        manager = self.get_serializer_context()['manager']
        if manager:
            queryset = self.queryset.filter(head=manager)
            serializer = self.serializer_class(
                queryset, many=True,
                context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        manager = self.get_serializer_context()['manager']

        if manager and instance.head == manager:
            serializer = self.serializer_class(
                instance,
                context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)

class HeadStatisticViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HeadStatisticSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        head_id = self.kwargs.get('head_id')
        return Manager.objects.filter(id=head_id)

class EmployeeStatisticViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmployeeStatisticSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        return Employee.objects.filter(id=employee_id)
