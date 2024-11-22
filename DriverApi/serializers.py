from rest_framework import serializers
from .models import Driver, DriverLocation, DriverRidesHistory,CurrentBooking

class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['id', 'first_name', 'last_name', 'email', 'number', 'auto_no', 'password']

class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = ['driver', 'latitude', 'longitude']

class DriverRidesHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverRidesHistory
        fields = ['driver', 'passenger', 'source_address', 'destination_address', 'booked_time', 'auto_no', 'passenger_name']
class CurrentBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentBooking
        fields = ['id', 'passenger', 'driver', 'source_address', 'destination_address', 'booked_time']
