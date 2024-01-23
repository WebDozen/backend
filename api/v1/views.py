from rest_framework.response import Response
from users.models import Employee
from api.v1.serializers import EmployeeSerializer
from rest_framework import viewsets, status


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_employee(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            return Response({'Сообщение': 'Сотрудник не найден'},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeSerializer(employee)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)
