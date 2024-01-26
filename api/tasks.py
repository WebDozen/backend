from celery import shared_task
from django.utils import timezone
from plans.models import IDP, ExecutionStatus


@shared_task()
def determine_status(ipr_id):
    instance = IDP.objects.get(pk=ipr_id)
    instance.execution_status = determine_status_function(instance)
    instance.save()


def determine_status_function(instance):
    if instance.deadline < timezone.now():  # если дедлайн просрочен
        status = ExecutionStatus.objects.get(slug='expired')
        instance.execution_status = status
    elif not instance.tasks.exclude(status='завершено').exists():
        # если все задачи завершены
        status = ExecutionStatus.objects.get(slug='review')
        instance.execution_status = status
    elif instance.tasks.filter(
        execution_status__in=['в работе', 'завершено']
    ).exists():
        # есть ли хотя бы одна задача в статусе 'в работе' или 'завершено'
        instance.execution_status = ExecutionStatus.objects.get(slug='work')
    return instance.execution_status
