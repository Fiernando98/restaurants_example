from drf_query_filter import fields
from rest_framework import viewsets

from .models import Foods
from .serializer import FoodsSerializer


class FoodsViewSet(viewsets.ModelViewSet):
    model = Foods
    serializer_class = FoodsSerializer
    queryset = model.objects.all()

    query_params = [
        fields.Field('restaurant', 'restaurant'),
        fields.Field('name', 'name__icontains')
    ]
