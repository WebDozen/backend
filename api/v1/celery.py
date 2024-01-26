from celery import Celery
from django.utils import timezone
from plans.models import IDP, ExecutionStatus

app = Celery('alfa_people')


@app.task
def determine_status(ipr_id):
    instance = IDP.objects.get(pk=ipr_id)
    instance.execution_status = determine_status_function(instance)


def determine_status_function(instance):
    if instance.deadline < timezone.now():  # если дедлайн просрочен
        status = ExecutionStatus.objects.get(slug='expired')
        instance.execution_status = status
        instance.save()
    elif not instance.tasks.exclude(status='завершено').exists():
        # если все задачи завершены
        status = ExecutionStatus.objects.get(slug='review')
        instance.execution_status = status
        instance.save()
    elif instance.tasks.filter(
        execution_status__in=['в работе', 'завершено']
    ).exists():
        # есть ли хотя бы одна задача в статусе 'в работе' или 'завершено'
        instance.execution_status = ExecutionStatus.objects.get(slug='work')
        instance.save()
