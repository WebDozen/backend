from django.test import TestCase
from django.utils import timezone
from plans.models import (
    Execution_status,
    IDP,
    Type_task,
    Task,
    idp_comment,
    task_comment
    )
from users.models import Manager, Employee, User


class BaseTestCase(TestCase):
    def setUp(self):
        """Устанавливает общие данные для всех тестовых классов."""

        self.execution_status = Execution_status.objects.create(
            name='In Progress',
            slug='in-progress'
        )
        self.manager_user = User.objects.create(
            email='test_manager@example.com',
            role=User.Role.MANAGER)
        self.manager = Manager.objects.create(user=self.manager_user)
        self.employee_user = User.objects.create(
            email='test_employee@example.com',
            role=User.Role.EMPLOYEE)
        self.employee = Employee.objects.create(
            user=self.employee_user,
            position='Test Position',
            grade='Test Grade',
            head=self.manager
        )

        self.idp = IDP.objects.create(
            author=self.manager,
            employee=self.employee,
            name='Test IDP',
            description='Test description',
            deadline=timezone.now() + timezone.timedelta(days=7),
            execution_status=self.execution_status,
            message='Test message'
        )


class ExecutionStatusModelTest(BaseTestCase):
    def test_execution_status_creation(self):
        """Проверяет создание объекта Execution_status."""

        execution_status = Execution_status.objects.create(
            name='Test Status',
            slug='test-status'
        )
        self.assertEqual(execution_status.name, 'Test Status')
        self.assertEqual(execution_status.slug, 'test-status')


class IDPModelTest(BaseTestCase):
    def test_idp_creation(self):
        """Проверяет создание объекта IDP."""

        type_task = Type_task.objects.create(
            name='Development',
            slug='development'
        )
        task = Task.objects.create(
            idp=self.idp,
            type=type_task,
            name='Test Task',
            description='Test task description',
            execution_status=self.execution_status
        )
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.description, 'Test task description')
        self.assertEqual(task.execution_status, self.execution_status)


class TypeTaskModelTest(BaseTestCase):
    def test_type_task_creation(self):
        """Проверяет создание объекта Type_task."""

        type_task = Type_task.objects.create(
            name='Test Type',
            slug='test-type'
        )
        self.assertEqual(type_task.name, 'Test Type')
        self.assertEqual(type_task.slug, 'test-type')


class IDPCommentModelTest(BaseTestCase):
    def test_idp_comment_creation(self):
        """Проверяет создание объекта IDPComment."""

        comment = idp_comment.objects.create(
            author=self.employee.user,
            text='Test IDP Comment',
            idp=self.idp
        )
        self.assertEqual(comment.text, 'Test IDP Comment')


class TaskCommentModelTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.type_task = Type_task.objects.create(
            name='Test Type_2',
            slug='test-type_2'
        )
        self.task = Task.objects.create(
            idp=self.idp,
            type=self.type_task,
            name='Test Task',
            description='Test task description',
            execution_status=self.execution_status
        )

    def test_task_comment_creation(self):
        """Проверяет создание объекта TaskComment."""

        comment = task_comment.objects.create(
            author=self.employee.user,
            text='Test Task Comment',
            task=self.task
        )
        self.assertEqual(comment.text, 'Test Task Comment')


class TaskModelTest(BaseTestCase):
    def test_task_creation(self):
        type_task = Type_task.objects.create(
            name='Development',
            slug='development'
        )
        task = Task.objects.create(
            idp=self.idp,
            type=type_task,
            name='Test Task',
            description='Test task description',
            execution_status=self.execution_status
        )
        self.assertEqual(task.name, 'Test Task')
        self.assertEqual(task.description, 'Test task description')
        self.assertEqual(task.execution_status, self.execution_status)
