from django.db.models.base import Model
from rest_framework import serializers
from .models import Plans, Subscription, PlanFeatures, SubscriptionUsed, PlansFeatureUser



class PlanFeaturesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PlanFeatures
        # fields = "__all__"
        fields = ('id', 'name', 'type', 'Value')

class PlanViewSerializer(serializers.ModelSerializer):
    features = PlanFeaturesSerializer(many=True, read_only=True)
    class Meta:
        model = Plans
        # fields = "__all__"
        fields = ('id','name', 'price', 'interval', 'product_id', 'price_id', 'lookup_key', 'currency', 'features')



class GetSubscriptionViewSerializer(serializers.Serializer):
    plans = serializers.IntegerField()
    # status = serializers.BooleanField()
    success_url = serializers.CharField(max_length=500)
    fail_url = serializers.CharField(max_length=500)

    # class Meta:
    #     model = Subscription
    #     # fields = '__all__'
    #     fields = ('id','plans','status',)

class GetSubscriptionViewbyuserSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlansFeatureUser
        fields = '__all__'
        # fields = "__all__"

class SubscriptionPlanUsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUsed
        fields = "__all__"