from django.shortcuts import render
from django.db.models import Prefetch, F, Avg, Sum
from rest_framework.viewsets import ReadOnlyModelViewSet

from services.models import Subscription
from clients.models import Client
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()\
        .prefetch_related(
        'plan',
        Prefetch('client', queryset=Client.objects.all()
                 .select_related('user')
                 .only('user__email', 'company_name')
                 )
    ).annotate(price=F('service__price') - F('service__price') * F('plan__discount_percent') / 100.00)

    serializer_class = SubscriptionSerializer

    # изменение вывода данных
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        response = super().list(request, *args, **kwargs)
        response_data = {'result': response.data}

        response_data['total_cost_amoint'] = queryset\
            .aggregate(total=Sum('price')).get('total')

        response.data = response_data

        return response
