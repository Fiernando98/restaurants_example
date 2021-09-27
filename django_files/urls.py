from django.contrib import admin
from django.urls import path
from django.urls import include
from apps.users.views import LoginCustomView
from knox.views import LogoutView, LogoutAllView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', LoginCustomView.as_view(), name='knox_custom_login'),
    path('auth/logout/', LogoutView.as_view(), name='knox_logout'),
    path('auth/logoutall/', LogoutAllView.as_view(), name='knox_logoutall'),
    path('restaurants/', include('apps.restaurants.urls')),
    path('foods/', include('apps.foods.urls'))
]
