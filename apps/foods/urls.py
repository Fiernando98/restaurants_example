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
    url(r'^$', Foods_list, name='foods_lists '),
    url(r'^(?P<pk>\d+)/$', Foods_details, name='foods_details '),
]
