from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import (
    viewsets,
    status,
    mixins,
    serializers
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    inline_serializer
)

from .permissions import (
    IsManagerOfEmployee,
    IsMentor,
    IsSelfEmployee,
    IsManagerandEmployee,
    IsEmployeeIDPExecutor)

from users.models import Employee, Manager
from plans.models import IDP, Task, StatusTask

from .serializers import (
    IDPCreateAndUpdateSerializer,
    IDPSerializer,
    IDPDetailSerializer,
    EmployeeSerializer,
    HeadStatisticSerializer,
    TaskStatusUpdateSerializer,
    TaskSerializer
)


@extend_schema(tags=['ИПР'])
@extend_schema_view(
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
        summary='Получение списка сотрудников '
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

    permission_classes = [IsAuthenticated, IsManagerandEmployee]
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.queryset.none()
        if hasattr(user, 'manager_profile'):
            if user.manager_profile:
                queryset = self.get_subordinates(user.manager_profile)
        elif hasattr(user, 'employee_profile'):
            mentor_idp = IDP.objects.filter(mentor=user.employee_profile)
            employee_ids = [idp.employee.id for idp in mentor_idp]
            queryset = Employee.objects.filter(id__in=employee_ids)
            if not queryset.exists():
                raise PermissionDenied(
                    'У вас нет прав доступа к этому ресурсу.'
                )

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_subordinates(self, manager):
        """Возвращает подчиненных сотрудников данного руководителя."""
        return Employee.objects.filter(head=manager)


@extend_schema(tags=['Статистика для руководителя'])
@extend_schema_view(
    list=extend_schema(
        summary='Получение статистики сотрудников по ИПР',
        methods=['GET'],
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='head_id',
                required=True,
                type=int
            ),
        ],
        description='Страница руководителя',
    )
)
class HeadStatisticViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = HeadStatisticSerializer
    permission_classes = [IsManagerandEmployee]

    def get_queryset(self):
        username = self.request.user.username
        queryset = get_object_or_404(Manager, user__username=username)
        return [queryset]

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(*serializer.data)


@extend_schema(tags=['Статусы'])
class TaskStatusChangeViewSet(viewsets.ViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsEmployeeIDPExecutor]
    queryset = Task.objects.all()

    @extend_schema(
        request=inline_serializer(
            name="InlineFormSerializer",
            fields={
                "status_slug": serializers.CharField()
            },
        ),
        responses={200: TaskSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='idp_id',
                required=True,
                type=int
            ),
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name='task_id',
                required=True,
                type=int
            ),
        ]
    )
    @action(detail=False, methods=['patch'])
    def status(self, request, idp_id, task_id):
        """Изменение статуса задачи."""
        print(request.data)
        new_status_slug = request.data['status_slug']
        new_status_id = get_object_or_404(StatusTask, slug=new_status_slug).id
        task = get_object_or_404(Task, idp=idp_id, id=task_id)
        serializer = TaskStatusUpdateSerializer(
            task, data={'status': new_status_id}, partial=True
        )
        if serializer.is_valid():
            serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
