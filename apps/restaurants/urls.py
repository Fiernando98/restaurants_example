from django.conf.urls import url
from .views import RestaurantsViewSet

restaurants_list = RestaurantsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

restaurants_details = RestaurantsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'^$', restaurants_list, name='restaurants_lists '),
    url(r'^(?P<pk>\d+)/$', restaurants_details, name='restaurants_details '),
]
