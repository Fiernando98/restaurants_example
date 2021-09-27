from django.conf.urls import url
from .views import FoodsViewSet

foods_list = FoodsViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

foods_details = FoodsViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    url(r'^$', foods_list, name='foods_lists '),
    url(r'^(?P<pk>\d+)/$', foods_details, name='foods_details '),
]
