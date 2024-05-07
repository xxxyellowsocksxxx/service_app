import time
import datetime
from celery_singleton import Singleton
from celery import shared_task
from django.db.models import F
from django.db import transaction


@shared_task(base=Singleton)
def set_price(subscribtion_id):
    from services.models import Subscription

    with transaction.atomic():
        # вычисление конечной цены услуги со скидкой
        subscription = Subscription.objects.select_for_update()\
            .filter(id=subscribtion_id)\
            .annotate(annotated_price=F('service__price') - (F('service__price') * F('plan__discount_percent') / 100.00))\
            .first()
        subscription.price = subscription.annotated_price
        # сохранение конкретно этого поля модели
        subscription.save(update_fields=['price'])
        # subscription.save()


@shared_task(base=Singleton)
def set_created_at(subscribtion_id):
    from services.models import Subscription

    with transaction.atomic():

        subscription = Subscription.objects.select_for_update().get(id=subscribtion_id)
        subscription.created_at = str(datetime.datetime.now())
        # сохранение конкретно этого поля модели
        subscription.save(update_fields=['created_at'])
