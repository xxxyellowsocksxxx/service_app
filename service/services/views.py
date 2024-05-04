from django.shortcuts import render
from django.db.models import Prefetch, F, Avg
from rest_framework.viewsets import ReadOnlyModelViewSet

from services.models import Subscription
from clients.models import Client
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all().prefetch_related('plan',
                                                           'client',
                                                           'client__user').only('client__user__email',
                                                                                'client__company_name',
                                                                                'plan_id')

    serializer_class = SubscriptionSerializer
