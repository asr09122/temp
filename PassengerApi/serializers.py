from rest_framework import serializers
from .models import Passenger, TravelHistory

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'first_name', 'last_name', 'email', 'number', 'roll_no', 'subgroup_year', 'password']

class TravelHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelHistory
        fields = ['passenger', 'driver', 'source_address', 'destination_address', 'booked_time', 'auto_no']
