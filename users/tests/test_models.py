from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from users.models import Employee, Manager, MentorEmployee, User


class BaseUserModelTest(TestCase):
    """Базовый тестовый класс для модели User."""

    def setUp(self):
        """Настройка экземпляра User для тестирования."""
        self.user = User.objects.create(
            first_name='John',
            middle_name='Doe',
            last_name='Smith',
            role=User.Role.EMPLOYEE,
            email='john_doe_employee@example.com'
        )


class UserModelTest(BaseUserModelTest):
    """Тестирование модели User."""

    def test_user_creation(self):
        """Тест успешного создания экземпляра User."""
        self.assertIsInstance(self.user, User)

    def test_user_str_method(self):
        """Тест строкового представления модели User."""
        expected_str = (f'{self.user.first_name}'
                        f'{self.user.middle_name}'
                        f'{self.user.last_name}'
                        f'({self.user.role})')
        self.assertEqual(str(self.user), expected_str)


class BaseManagerModelTest(BaseUserModelTest):
    """Базовый тестовый класс для модели Manager."""

    def setUp(self):
        """Настройка экземпляра Manager для тестирования."""
        super().setUp()
        self.user.role = User.Role.MANAGER
        self.user.email = 'john_doe_manager@example.com'
        self.user.save()
        self.manager = Manager.objects.create(user=self.user)


class ManagerModelTest(BaseManagerModelTest):
    """Тестирование модели Manager."""

    def test_manager_creation(self):
        """Тест успешного создания экземпляра Manager."""
        self.assertIsInstance(self.manager, Manager)

    def test_manager_str_method(self):
        """Тест строкового представления модели Manager."""
        expected_str = (f'Руководитель: {self.manager.user.first_name}'
                        f'{self.manager.user.middle_name}'
                        f'{self.manager.user.last_name}'
                        f'({self.manager.user.role})')
        self.assertEqual(str(self.manager), expected_str)


class BaseEmployeeModelTest(BaseManagerModelTest):
    """Базовый тестовый класс для модели Employee."""

    def setUp(self):
        """Настройка экземпляра Employee для тестирования."""
        super().setUp()
        self.user.role = User.Role.EMPLOYEE
        self.user.email = 'john_doe_employee@example.com'
        self.user.save()
        self.employee = Employee.objects.create(
            user=self.user,
            position='Developer',
            grade='Junior',
            head=self.manager
        )


class EmployeeModelTest(BaseEmployeeModelTest):
    """Тестирование модели Employee."""

    def test_employee_creation(self):
        """Тест успешного создания экземпляра Employee."""
        self.assertIsInstance(self.employee, Employee)

    def test_employee_user_relation(self):
        """Тест связи пользователя и сотрудника."""
        self.assertEqual(self.employee.user, self.user)

    def test_employee_str_method(self):
        """Тест строкового представления модели Employee."""
        expected_str = (f'Сотрудник: {self.employee.user.first_name}'
                        f'{self.employee.user.middle_name}'
                        f'{self.employee.user.last_name}'
                        f'({self.employee.user.role})')
        self.assertEqual(str(self.employee), expected_str)


class BaseMentorEmployeeModelTest(BaseEmployeeModelTest):
    """Базовый тестовый класс для модели MentorEmployee."""

    def setUp(self):
        """Настройка экземпляра MentorEmployee для тестирования."""
        super().setUp()
        self.mentor_user = User.objects.create(
            first_name='Mentor',
            middle_name='Doe',
            last_name='Smith',
            role=User.Role.EMPLOYEE,
            email='mentor_doe@example.com'
        )
        self.mentor = Employee.objects.create(
            user=self.mentor_user,
            position='Senior Developer',
            grade='Senior',
            head=self.manager
        )
        self.mentee_user = User.objects.create(
            first_name='Mentee',
            middle_name='Doe',
            last_name='Smith',
            role=User.Role.EMPLOYEE,
            email='mentee_doe@example.com'
        )
        self.mentee = Employee.objects.create(
            user=self.mentee_user,
            position='Junior Developer',
            grade='Junior',
            head=self.manager
        )


class MentorEmployeeModelTest(BaseMentorEmployeeModelTest):
    """Тестирование модели MentorEmployee."""

    def test_mentor_employee_creation(self):
        """Тест успешного создания экземпляра MentorEmployee."""
        mentor_employee = MentorEmployee.objects.create(mentor=self.mentor,
                                                        mentee=self.mentee)
        self.assertIsInstance(mentor_employee, MentorEmployee)

    def test_mentor_employee_relations(self):
        """Тест связей между ментором и сотрудником."""
        mentor_employee = MentorEmployee.objects.create(mentor=self.mentor,
                                                        mentee=self.mentee)
        self.assertEqual(mentor_employee.mentor, self.mentor)
        self.assertEqual(mentor_employee.mentee, self.mentee)

    def test_mentor_employee_clean_method(self):
        """Тест функции clean модели MentorEmployee."""
        with self.assertRaises(ValidationError) as context:
            mentor_employee = MentorEmployee(mentor=self.mentee,
                                             mentee=self.mentee)
            mentor_employee.clean()

        self.assertEqual(
            str(context.exception.messages[0]),
            "Сотрудник не может быть своим ментором."
        )

    def test_mentor_employee_unique_constraint(self):
        """Тест уникальности связи между ментором и сотрудником."""
        MentorEmployee.objects.create(mentor=self.mentor,
                                      mentee=self.mentee)

        with self.assertRaises(IntegrityError):
            MentorEmployee.objects.create(mentor=self.mentor,
                                          mentee=self.mentee)
