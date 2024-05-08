from typing import Iterable
from django.db import models
from django.core.validators import MaxValueValidator

from clients.models import Client
from services.tasks import set_price, set_created_at


# услуги. названия и цены
class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # запись стартового значения цены
        self.__price = self.price

    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating:
            return result

        # проверка на наличие изменений в цене
        if self.price != self.__price:
            for sub in self.subscriptions.all():
                set_price.delay(sub.id)
                set_created_at.delay(sub.id)

        return result


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # запись стартового значения процента скидки
        self.__discount_percent = self.discount_percent

    def save(self, *args, **kwargs):
        # проверка на существование объекта
        creating = not bool(self.id)
        # result = super().save(*args, **kwargs)
        if creating:
            super().save(*args, **kwargs)

        # проверка на наличие изменений в проценте скидки
        if self.discount_percent != self.__discount_percent:
            for sub in self.subscriptions.all():
                set_price.delay(sub.id)
                set_created_at.delay(sub.id)

        # super().save(*args, **kwargs)

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
        if creating:
            set_price.delay(self.id)
            set_created_at.delay(self.id)

        return super().save(*args, **kwargs)
