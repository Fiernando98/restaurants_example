from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurants/', include('apps.restaurants.urls')),
    path('foods/', include('apps.foods.urls'))
]
