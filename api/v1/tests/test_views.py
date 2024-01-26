from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Employee


class EmployeeViewSetTests(TestCase):

    def setUp(self):
        self.manager = get_user_model().objects.create_user(
            username='manager_test',
            first_name='John',
            middle_name='Doe',
            last_name='Manager',
            email='manager@example.com',
            role='manager',
        )
        self.employee_data = {
            'user': get_user_model().objects.create_user(
                username='employee_test',
                first_name='Danila',
                middle_name='Danilovich',
                last_name='Danilov',
                email='danila@example.com',
                role='employee',
            ),
            'position': 'Developer',
            'grade': 'Senior',
        }
        self.employee = Employee.objects.create(**self.employee_data)
        self.client.force_authenticate(user=self.manager)
        self.url = f'/v1/employees/{self.employee.id}/'

    def tearDown(self):
        self.manager.delete()

    def test_get_employee_by_manager(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_employee_by_employee(self):
        unauthorized_client = APIClient()
        response = unauthorized_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)