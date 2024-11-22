from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/passenger/', include('PassengerApi.urls')),
    path('api/driver/', include('DriverApi.urls')),
]
