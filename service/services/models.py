from django.db import models
from django.core.validators import MaxValueValidator

from clients.models import Client

# услуги. названия и цены


class Service(models.Model):
    name = models.CharField(max_length=50)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name

# тарифные планы скидок


class Plan(models.Model):
    PLAN_TYPES = (
        ('full', 'Full'),
        ('student', 'Student'),
        ('discount', 'Discount')
    )

    plan_type = models.CharField(choices=PLAN_TYPES, max_length=50)
    discount_percent = models.PositiveIntegerField(default=0,
                                                   validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.plan_type

# информация о подписке, кто на какую услугу, какой таринфный план


class Subscription(models.Model):
    client = models.ForeignKey(
        Client, related_name='subscriptions', on_delete=models.PROTECT)
    service = models.ForeignKey(
        Service, related_name='subscriptions', on_delete=models.PROTECT)
    plan = models.ForeignKey(
        Plan, related_name='subscriptions', on_delete=models.PROTECT)
