from rest_framework.response import Response
from users.models import Employee, Manager
from api.v1.serializers import EmployeeSerializer
from rest_framework import viewsets, status


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
