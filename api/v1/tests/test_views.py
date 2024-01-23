from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Employee
from plans.models import IDP, Execution_status


class EmployeeViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'first_name': 'Danila',
            'middle_name': 'Danilovich',
            'last_name': 'Danilov',
            'email': 'danila@example.com',
            'role': 'employee',
        }
        self.user = get_user_model().objects.create(**self.user_data)
        self.employee_data = {
            'user': self.user,
            'position': 'Developer',
            'grade': 'Senior',
        }
        self.employee = Employee.objects.create(**self.employee_data)

        self.execution_status = Execution_status.objects.create(
            name='В РАБОТЕ'
            )

        self.idp_data = {
            'author': None,
            'employee': self.employee,
            'name': 'IDP Test',
            'description': 'Test IDP description',
            'deadline': '2024-01-31T12:00:00Z',
            'execution_status': self.execution_status,
            'message': 'Test motivational message',
        }
        self.idp = IDP.objects.create(**self.idp_data)

    def test_get_employee(self):
        url = f'/v1/employees/{self.employee.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_employee_not_found(self):
        url = '/v1/employees/999/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
