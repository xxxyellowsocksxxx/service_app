from django.db.models import Prefetch, Sum
from django.core.cache import cache
from django.conf import settings

from rest_framework.viewsets import ReadOnlyModelViewSet


from services.models import Subscription, Service
from clients.models import Client
from services.serializers import SubscriptionSerializer


class SubscriptionView(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()\
        .prefetch_related(
        'plan',
        Prefetch('service', queryset=Service.objects.all()),
        Prefetch('client', queryset=Client.objects.all()
                 .select_related('user')
                 .only('user__email', 'company_name')
                 ))\

    serializer_class = SubscriptionSerializer

    # изменение структуры вывода json в виде словаря списков (объект массивов)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        response = super().list(request, *args, **kwargs)

        # получение данных из кеша
        price_cache = cache.get(settings.PRICE_CACHE_NAME)
        # проверка на наличие данных, если их нет тогда они рассчитаются и туда попадут
        if price_cache:
            total_price = price_cache
        else:
            total_price = queryset\
                .aggregate(total=Sum('price')).get('total')
            cache.set(settings.PRICE_CACHE_NAME, total_price, 60*60)

        # дефолтные данные теперь нахоядятся тут, в списке объектов
        response_data = {'result': response.data}
        # рассчитывается сумма оплаченых подписок
        response_data['total_cost_amount'] = total_price

        response.data = response_data

        return response
