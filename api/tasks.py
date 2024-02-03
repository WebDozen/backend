# from datetime import timedelta
from celery import shared_task
from celery.schedules import crontab
from django.utils import timezone
from alfa_people.celery import app as celery_app
from celery.utils.log import get_task_logger
from django.db.models import Max, F, OuterRef, Subquery

from plans.models import IDP, StatusIDP


logger = get_task_logger(__name__)


@shared_task()
def determine_status_idp_by_task(idp_id):
    """Запускает проверку статуса ИПР после изменения статуса задачи в ИПР"""
    instance = IDP.objects.get(pk=idp_id)
    if instance.task.exists():
        instance.status = determine_status_idp(instance)
        instance.save()


def determine_status_idp(instance):
    """Проверяет какой статус у ИПР должен быть"""
    if not instance.task.exclude(status__slug='completed').exists():
        return StatusIDP.objects.get(slug='awaiting_review')
    elif instance.task.filter(
        status__slug__in=['in_progress', 'completed']
    ).exists():
        return StatusIDP.objects.get(slug='in_progress')


@shared_task()
def check_idp_statuses_by_deadline():
    """Запускает проверку ИПР по дедлайну"""
    try:
        latest_idps = IDP.objects.annotate(
            max_pub_date=Max('pub_date')
        ).filter(
            pub_date=F('max_pub_date')
        ).order_by('employee', '-pub_date')

        subquery = latest_idps.filter(
            employee=OuterRef('employee')
        ).values('id')[:1]

        result = IDP.objects.filter(id__in=Subquery(subquery))

        new_status = StatusIDP.objects.get(slug='expired')
        for idp in result:
            if (
                idp.status.slug in ['open', 'in_progress', 'awaiting_review']
                and idp.deadline
                and idp.deadline < timezone.now()
            ):
                print(timezone.now())
                idp.status = new_status
                idp.save()
    except Exception as e:
        logger.error(f'Error in check_idp_statuses: {e}', exc_info=True)


celery_app.conf.beat_schedule = {
    'check-idp-statuses': {
        'task': 'api.tasks.check_idp_statuses_by_deadline',
        'schedule': crontab(hour=23, minute=0),
        # 'schedule': timedelta(seconds=20),
    },
}
