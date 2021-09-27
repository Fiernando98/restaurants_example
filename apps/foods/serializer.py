from rest_framework import serializers
from .models import Foods
from apps.restaurants.models import Restaurants
from apps.restaurants.serializer import RestaurantsSerializer
from lib.reusable import PkRelatedSerializerField


class FoodsSerializer(serializers.ModelSerializer):
    restaurant = PkRelatedSerializerField(queryset=Restaurants.objects.all(), required=True,
                                          instance_serializer=RestaurantsSerializer())

    class Meta:
        model = Foods
        fields = '__all__'
