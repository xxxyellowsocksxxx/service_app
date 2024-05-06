from django.db.models import Prefetch, Sum
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
    )

    serializer_class = SubscriptionSerializer

    # изменение структуры вывода json в виде словаря списков (объект массивов)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        response = super().list(request, *args, **kwargs)

        # дефолтные данные теперь нахоядятся тут, в списке объектов
        response_data = {'result': response.data}
        # рассчитывается сумма оплаченых подписок
        response_data['total_cost_amoint'] = queryset\
            .aggregate(total=Sum('price')).get('total')

        response.data = response_data

        return response
