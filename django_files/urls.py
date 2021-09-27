from django.contrib import admin
from django.urls import include
from django.urls import path
from knox.views import LogoutView, LogoutAllView

from apps.users.views import LoginCustomView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login/', LoginCustomView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/logout_all/', LogoutAllView.as_view()),
    path('restaurants/', include('apps.restaurants.urls')),
    path('foods/', include('apps.foods.urls'))
]
