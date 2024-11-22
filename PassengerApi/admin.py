from django.contrib import admin
from .models import Passenger, TravelHistory

# Registering models with simple admin.site.register
admin.site.register(Passenger)
admin.site.register(TravelHistory)
