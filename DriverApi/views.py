from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from .models import Driver, DriverLocation, DriverRidesHistory, CurrentBooking
from PassengerApi.models import TravelHistory
from .serializers import DriverSerializer, DriverLocationSerializer, DriverRidesHistorySerializer, CurrentBookingSerializer
from PassengerApi.serializers import TravelHistorySerializer

def authenticate_token(request):
    token_key = request.META.get('HTTP_AUTHORIZATION')
    if token_key is None:
        raise AuthenticationFailed("Authentication credentials were not provided.")

    try:
        token = token_key.split()[1] 
        token_obj = Token.objects.get(key=token)
        return token_obj.user
    except (Token.DoesNotExist, IndexError):
        raise AuthenticationFailed("Invalid token.")
class SignupDriver(APIView):
    def post(self, request):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        number = request.data.get('number')
        auto_no = request.data.get('auto_no')

        try:
            user = User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            driver = Driver.objects.create(
                user=user,
                number=number,
                auto_no=auto_no,
                first_name=first_name,
                last_name=last_name,
                email=email
            )

            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Driver registered successfully",
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginDriver(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "message": "Login successful",
                    "token": token.key
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutDriver(APIView):
    def post(self, request):
        user = authenticate_token(request)
        driver = get_object_or_404(Driver, user=user)

        try:
            # Clear any current bookings for the driver
            CurrentBooking.objects.filter(driver=driver).delete()
            Token.objects.get(user=user).delete()  # Delete the token on logout
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UpdateDriverLocation(APIView):
    def put(self, request):
        user = authenticate_token(request)
        driver = get_object_or_404(Driver, user=user)

        # Check if the driver has a current booking
        if CurrentBooking.objects.filter(driver=driver).exists():
            return Response({"error": "You cannot update your location while you have a current booking."}, status=status.HTTP_400_BAD_REQUEST)

        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        if latitude is None or longitude is None:
            return Response({"error": "Latitude and longitude are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            driver_location = DriverLocation.objects.get(driver=driver)
            driver_location.latitude = latitude
            driver_location.longitude = longitude
            driver_location.save()
            return Response({"message": "Driver location updated successfully"}, status=status.HTTP_200_OK)
        except DriverLocation.DoesNotExist:
            DriverLocation.objects.create(driver=driver, latitude=latitude, longitude=longitude)
            return Response({"message": "Driver location created successfully"}, status=status.HTTP_201_CREATED)
   

class DriverRidesHistoryView(APIView):
    def get(self, request):
        user = authenticate_token(request)

        driver = get_object_or_404(Driver, user=user)

        rides = DriverRidesHistory.objects.filter(driver=driver)
        
        serializer = DriverRidesHistorySerializer(rides, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class CompleteRide(APIView):
    def post(self, request):
        user = authenticate_token(request)  
        driver = get_object_or_404(Driver, user=user)
        ride_id = request.data.get('ride_id')
        
        try:
            current_booking = CurrentBooking.objects.get(id=ride_id, driver=driver)
            
            passenger_travel_history = TravelHistory(
                passenger=current_booking.passenger,
                driver=current_booking.driver,
                source_address=current_booking.source_address,
                destination_address=current_booking.destination_address,
                booked_time=current_booking.booked_time,
                auto_no=current_booking.driver.auto_no
            )
            passenger_travel_history.save()

            driver_travel_history = DriverRidesHistory(
                passenger=current_booking.passenger,
                driver=current_booking.driver,
                source_address=current_booking.source_address,
                destination_address=current_booking.destination_address,
                booked_time=current_booking.booked_time,
                auto_no=current_booking.driver.auto_no,
                passenger_name=f"{current_booking.passenger.first_name} {current_booking.passenger.last_name}"
            )
            driver_travel_history.save()

            current_booking.delete()

            return Response({"message": "Ride marked as completed"}, status=status.HTTP_200_OK)
        except CurrentBooking.DoesNotExist:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelRide(APIView):
    def post(self, request):
        user = authenticate_token(request)
        ride_id = request.data.get('ride_id')
        dr=get_object_or_404(Driver,user=user)
        try:
            current_booking = CurrentBooking.objects.get(id=ride_id, driver=dr)
            current_booking.delete()
            return Response({"message": "Ride canceled successfully"}, status=status.HTTP_200_OK)
        except CurrentBooking.DoesNotExist:
            return Response({"error": "Ride not found"}, status=status.HTTP_404_NOT_FOUND)


class CurrentBookedRide(APIView):
    def get(self, request):
        user = authenticate_token(request) 

        driver = get_object_or_404(Driver, user=user)

        current_rides = CurrentBooking.objects.filter(driver=driver)

        if current_rides.exists():
            serializer = CurrentBookingSerializer(current_rides, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No current booked rides found."}, status=status.HTTP_404_NOT_FOUND)

