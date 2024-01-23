from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from plans.models import IDP
from users.models import Employee
from .serializers import IDPSerializer


class IDPViewSet(viewsets.ModelViewSet):
    serializer_class = IDPSerializer

    def get_queryset(self):
        employee_id = self.kwargs.get('employee_id')
        employee = get_object_or_404(Employee, id=employee_id)
        return IDP.objects.filter(employee=employee)
