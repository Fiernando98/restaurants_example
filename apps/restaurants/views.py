from drf_query_filter import fields
from rest_framework import viewsets

from .models import Restaurants
from .serializer import RestaurantsSerializer


class RestaurantsViewSet(viewsets.ModelViewSet):
    model = Restaurants
    serializer_class = RestaurantsSerializer
    queryset = model.objects.all()

    query_params = [
        fields.Field('name', 'name__icontains')
    ]
