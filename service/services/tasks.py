import time
from celery_singleton import Singleton
from celery import shared_task
from django.db.models import F


@shared_task(base=Singleton)
def set_price(subscribtion_id):
    from services.models import Subscription
    # имитация нагрузки
    time.sleep(8)

    # вычисление конечной цены услуги со скидкой
    subscription = Subscription.objects.filter(id=subscribtion_id)\
        .annotate(annotated_price=F('service__price') - F('service__price') * F('plan__discount_percent') / 100.00)\
        .first()
    subscription.price = subscription.annotated_price
    # сохранение конкретно этого поля модели
    subscription.save(update_fields=['price'])
