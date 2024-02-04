from django.core.management.base import BaseCommand
from users.models import User, Manager, Employee
import json


class Command(BaseCommand):
    help = 'Update data users'

    def handle(self, *args, **options):
        with open('manager_employee_dump.json', encoding='utf8') as file:
            data = json.load(file)

        for entry in data:
            model_name = entry.get('model')
            pk = entry.get('pk')
            fields = entry.get('fields')
            if model_name == 'users.manager':
                user_username = fields.get('user')
                try:
                    manager = Manager.objects.get(pk=pk)
                    for field, value in fields.items():
                        if field != 'user':
                            setattr(manager, field, value)
                    manager.user = User.objects.get(id=user_username)
                    manager.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Manager {user_username} updated')
                    )
                except Manager.DoesNotExist:
                    manager = Manager(
                        pk=pk,
                        user=User.objects.get(username=user_username),
                        **fields
                    )
                    manager.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Manager {user_username} created')
                    )
            elif model_name == 'users.employee':
                user_id = fields.get('user')
                head_id = fields.get('head')

                try:
                    employee = Employee.objects.get(pk=pk)
                    for field, value in fields.items():
                        if field == 'head' and head_id is not None:
                            employee.head = Manager.objects.get(pk=head_id)
                        elif field != 'user':
                            setattr(employee, field, value)
                    employee.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Employee {user_id} updated')
                    )
                except Employee.DoesNotExist:
                    employee = Employee(
                        pk=pk,
                        user=User.objects.get(username=user_id),
                        **fields
                    )
                    employee.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Employee {user_id} created')
                    )
