from django.core.management.base import BaseCommand
from russian_names import RussianNames

from users.models import User, Employee, MentorEmployee
from plans.models import ExecutionStatus
from api.constants import status_dict


def clear_data(self):
    """Удаление всех аккаунтов в базе."""
    User.objects.all().delete()
    ExecutionStatus.objects.all().delete()
    self.stdout.write(
        self.style.WARNING('Данные удалены.')
    )


def create_test_user(role):
    """Создание тестового пользователя."""
    password = 'test_password'
    first_name, middle_name, last_name = RussianNames().get_person().split(' ')
    username = f'{last_name}_{first_name[0]}.{last_name[0]}.'
    user = User.objects.get_or_create(
        username=username, password=password,
        first_name=first_name, middle_name=middle_name,
        last_name=last_name,
        role=role
    )
    return user


class Command(BaseCommand):
    help = "Загружает данные тестовых пользователей."

    def add_arguments(self, parser):
        # Аргумент для удаления всех имеющихся в БД данных
        parser.add_argument(
            '--delete-existing',
            action='store_true',
            dest='delete_existing',
            default=False,
            help='Удаляет предыдущие данные',
        )

    def handle(self, *args, **options):
        """Загрузка данных."""

        if options['delete_existing']:
            clear_data(self)
            return
        for _ in range(5):
            """Создаем 5 руководителей."""
            create_test_user(User.Role.MANAGER)
        for _ in range(10):
            """Создаем 10 сотрудников."""
            create_test_user(User.Role.EMPLOYEE)
        for name, slug in status_dict.items():
            """Загружаем статусы задач/ИПР."""
            ExecutionStatus.objects.get_or_create(
                name=name, slug=slug
            )
        return self.stdout.write(
            self.style.SUCCESS('Тестовые данные сохранены')
        )
