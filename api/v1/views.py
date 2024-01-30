from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    )

from users.models import Employee, Manager
from plans.models import IDP
from .permissions import IsManagerOfEmployee, IsMentor, IsSelfEmployee
from .serializers import (
    IDPCreateAndUpdateSerializer,
    IDPSerializer,
    IDPDetailSerializer,
    EmployeeSerializer
)


@extend_schema(tags=['ИПР'])
@extend_schema_view(
    tags=['ИПР'],
    list=extend_schema(
        summary='Получение всех ИПР сотрудника',
        methods=['GET'],
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='employee_id',
                required=True,
                type=int
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Получение ИПР сотрудника',
        methods=['GET'],
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='employee_id',
                required=True,
                type=int
            ),
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='id',
                required=True,
                type=int
            ),
        ],
    ),
    partial_update=extend_schema(
        summary='Обновление данных ИПР',
        methods=['PATCH'],
        request=IDPCreateAndUpdateSerializer,
        responses={
            status.HTTP_200_OK: IDPDetailSerializer
        },
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='employee_id',
                required=True,
                type=int
            ),
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='id',
                required=True,
                type=int
            ),
        ],
    ),
    create=extend_schema(
        summary='Создание нового ИПР',
        methods=['POST'],
        request=IDPCreateAndUpdateSerializer,
        responses={
            status.HTTP_200_OK: IDPDetailSerializer
        },
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='employee_id',
                required=True,
                type=int
            ),
        ],
    ),
)
class IDPViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsManagerOfEmployee | IsSelfEmployee | IsMentor]

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

        if (
            self.request.user.role == 'manager' or
            self.request.user.id == employee.id
        ):
            return IDP.objects.filter(
                employee=employee
            ).prefetch_related('task')
        else:
            return IDP.objects.filter(
                employee=employee,
                mentor=self.request.user.id
            ).prefetch_related('task')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'employee_id': self.kwargs.get('employee_id')})
        return context

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsManagerOfEmployee]
        elif self.action == 'partial_update':
            self.permission_classes = [IsManagerOfEmployee | IsMentor]
        return [permission() for permission in self.permission_classes]


@extend_schema(tags=['Пользователи сервиса ИПР'],)
@extend_schema_view(
    list=extend_schema(
        summary='Получение списка сотрудников'
        'с данными по последнему ИПР',
        methods=['GET'],
        parameters=[
            OpenApiParameter(name='id', required=True, type=int),
        ],
        description='Страница руководителя',
    ),
    retrieve=extend_schema(
        summary='Получение всех данных о сотруднике',
        methods=['GET'],
    ),
)
class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для просмотра сотрудников."""

    permission_classes = [IsAuthenticated, IsManagerOfEmployee]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = ['get']

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
                queryset,
                many=True,
                context=self.get_serializer_context())
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer_context = self.get_serializer_context()

        serializer_context['exclude_mentor_and_status'] = True
        serializer = self.serializer_class(
            instance,
            context=serializer_context)
        return Response(serializer.data, status=status.HTTP_200_OK)
