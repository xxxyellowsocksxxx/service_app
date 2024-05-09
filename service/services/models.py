from typing import Iterable

from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models.signals import post_delete


from clients.models import Client
from services.tasks import set_price, set_created_at
from services.receivers import delete_cache_total_sum


# услуги. названия и цены
class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    # запись стартового значения цены
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__price = self.price

    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        if creating:
            return super().save(*args, **kwargs)

        # проверка на наличие изменений в цене
        if self.price != self.__price:
            for sub in self.subscriptions.all():
                set_price.delay(sub.id)
                set_created_at.delay(sub.id)

        return super().save(*args, **kwargs)


# тарифные планы скидок
class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )
    # список типов подписки
    plan_type = models.CharField(choices=PLAN_TYPES, max_length=50)
    # максимальное значение = 100
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.plan_type

    # запись стартового значения процента скидки
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        # проверка на существование объекта
        creating = not bool(self.id)
        if creating:
            return super().save(*args, **kwargs)

        # проверка на наличие изменений в проценте скидки
        if self.discount_percent != self.__discount_percent:
            for sub in self.subscriptions.all():
                set_price.delay(sub.id)
                set_created_at.delay(sub.id)

        return super().save(*args, **kwargs)


# информация о подписке, кто на какую услугу, какой таринфный план
class Subscription(models.Model):
    client = models.ForeignKey(
        Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(
        Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(
        Plan, related_name='subscriptions', on_delete=models.PROTECT)
    price = models.FloatField(default=0)
    created_at = models.CharField(max_length=50, blank=True, null=True)

    # рассчёт цены со скидкой при создании
    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating:
            set_price.delay(self.id)
            set_created_at.delay(self.id)

        return result


post_delete.connect(delete_cache_total_sum, sender=Subscription)
