from datetime import timedelta
from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from plans.models import IDP, StatusIDP
from alfa_people.celery import app as celery_app
from celery.utils.log import get_task_logger
from django.core.exceptions import ObjectDoesNotExist

logger = get_task_logger(__name__)


@shared_task()
def determine_status(ipr_id):
    instance = IDP.objects.get(pk=ipr_id)
    instance.status = determine_status_function(instance)
    instance.save()


@shared_task()
def check_idp_statuses():
    try:
        # print('start')
        # Получаем все объекты IDP, которые нуждаются в проверке статуса
        idps_to_check = IDP.objects.filter(
            status__slug__in=['open', 'work', 'review']
        )
        # print(idps_to_check)

        for idp in idps_to_check:
            print('start determine_status_function')
            determine_status_function(idp)
            print('end determine_status_function')
            # idp.save()
    except Exception as e:
        logger.error(f'Error in check_idp_statuses: {e}', exc_info=True)


def determine_status_function(instance):
    print('in determine_status_function')
    # if instance.deadline < timezone.now():  # если дедлайн просрочен
    #     status = StatusIDP.objects.get(slug='expired')
    #     instance.status = status
    # elif not instance.task.exclude(status='завершено').exists():
    #     # если все задачи завершены
    #     status = StatusIDP.objects.get(slug='review')
    #     instance.status = status
    # elif instance.task.filter(
    #     status__in=['в работе', 'завершено']
    # ).exists():
    #     # есть ли хотя бы одна задача в статусе 'в работе' или 'завершено'
    #     instance.status = StatusIDP.objects.get(slug='work')
    try:
        status = StatusIDP.objects.get(slug='expired')
        IDP.objects.filter(id=instance.id).update(status=status)

        print('Save successful')
        instance.refresh_from_db()
        print('Refresh from DB successful')
    except ObjectDoesNotExist:
        print('Status with slug "expired" does not exist')
    except Exception as e:
        print(f'Error during save: {e}')


celery_app.conf.beat_schedule = {
    'check-idp-statuses': {
        'task': 'api.tasks.check_idp_statuses',
        # 'schedule': crontab(minute='*/1'),
        'schedule': timedelta(seconds=10),
    },
}
