from django.contrib import admin
from .models import Driver, DriverLocation, DriverRidesHistory,CurrentBooking

# Registering models with simple admin.site.register
admin.site.register(Driver)
admin.site.register(DriverLocation)
admin.site.register(DriverRidesHistory)
admin.site.register(CurrentBooking)
