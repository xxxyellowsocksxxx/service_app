from rest_framework import serializers
from services.models import Subscription, Plan, Service


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer()

    service_name = serializers.CharField(source='service.name')

    client_name = serializers.CharField(source='client.company_name')
    email = serializers.CharField(source='client.user.email')
    # price = serializers.SerializerMethodField()

    # # задаёт стартовую цену подписки в аннотированное поле
    # def get_price(self, instance):
    #     return instance.price

    class Meta:
        model = Subscription
        fields = ('id', 'plan_id', 'service_name',
                  'client_name', 'email', 'plan', 'price', 'created_at')
