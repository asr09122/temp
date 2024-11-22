from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from .models import Passenger, TravelHistory
from DriverApi.models import DriverLocation, CurrentBooking,Driver
from .serializers import PassengerSerializer, TravelHistorySerializer
from DriverApi.serializers import DriverLocationSerializer, CurrentBookingSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Helper function to authenticate user using token
def authenticate_token(request):
    token_key = request.META.get('HTTP_AUTHORIZATION')
    if token_key is None:
        raise AuthenticationFailed("Authentication credentials were not provided.")

    # Extract token from the header
    try:
        token = token_key.split()[1]  # Assuming the format is "Token <token>"
        token_obj = Token.objects.get(key=token)
        return token_obj.user  # Return the authenticated user
    except (Token.DoesNotExist, IndexError):
        raise AuthenticationFailed("Invalid token.")

class SignupPassenger(APIView):
    def post(self, request):
        # Extract the relevant data from the request
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        number = request.data.get('number')
        roll_no = request.data.get('roll_no')
        subgroup_year = request.data.get('subgroup_year')

        # Check if email already exists in User
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create the User instance
            user = User.objects.create_user(
                username=email,  # Use email as username
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Now create the Passenger instance
            passenger = Passenger.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                number=number,
                roll_no=roll_no,
                subgroup_year=subgroup_year
            )

            # Generate an auth token for the user
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Passenger registered successfully",
                "token": token.key
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginPassenger(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            passenger = User.objects.get(email=email)
            if passenger.check_password(password):
                token, _ = Token.objects.get_or_create(user=passenger)  # Get or create a token
                return Response({"message": "Login successful", "token": token.key}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Passenger.DoesNotExist:
            return Response({"error": "Passenger not found"}, status=status.HTTP_404_NOT_FOUND)

class LogoutPassenger(APIView):
    def post(self, request):
        user = authenticate_token(request)
        passenger = get_object_or_404(Passenger, user=user)

        try:
            # Clear any current bookings for the passenger
            CurrentBooking.objects.filter(passenger=passenger).delete()
            Token.objects.get(user=user).delete()  # Delete the token on logout
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

class BookRide(APIView):
    def post(self, request):
        user = authenticate_token(request)  # Get the user from the token
        driver_id = request.data.get('driver')  # Get the driver ID from the request data
        ps=get_object_or_404(Passenger,user=user)

        # Check if driver_id is provided
        if not driver_id:
            return Response({"error": "Driver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the Passenger instance associated with the authenticated user
            

            # Fetch the Driver instance based on driver_id
            driver = Driver.objects.get(id=driver_id)  # Ensure this driver exists

            # Get booking details from the request
            source_address = request.data.get('source_address')
            destination_address = request.data.get('destination_address')

            # Create a new CurrentBooking instance
            current_booking = CurrentBooking.objects.create(
                passenger=ps,
                driver=driver,  # Assign the Driver instance here
                source_address=source_address,
                destination_address=destination_address
            )

            return Response({"message": "Ride booked successfully"}, status=status.HTTP_201_CREATED)

        except Passenger.DoesNotExist:
            return Response({"error": "Passenger not found"}, status=status.HTTP_404_NOT_FOUND)
        except Driver.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from django.shortcuts import get_object_or_404

class CancelRide(APIView):
    def post(self, request):
        user = authenticate_token(request)  # Authenticate the user
        ride_id = request.data.get('ride_id')
        ps=get_object_or_404(Passenger,user=user)

        try:
            current_booking = CurrentBooking.objects.get(id=ride_id, passenger=ps)
            current_booking.delete()  # Or mark it as canceled if you prefer
            return Response({"message": "Ride canceled successfully"}, status=status.HTTP_200_OK)
        except CurrentBooking.DoesNotExist:
            return Response({"error": "Ride not found or you do not have permission to cancel it"}, status=status.HTTP_404_NOT_FOUND)

class FindNearbyDrivers(APIView):
    def post(self, request):
        user = authenticate_token(request)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        radius = request.data.get('radius', 5)

        if latitude is None or longitude is None:
            return Response({"error": "Latitude and longitude must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except ValueError:
            return Response({"error": "Latitude, longitude, and radius must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)

        # Exclude drivers who have a current booking
        nearby_drivers = DriverLocation.objects.exclude(driver__in=CurrentBooking.objects.values_list('driver', flat=True))
        nearby_drivers = nearby_drivers.filter(
            latitude__gte=latitude - radius,
            latitude__lte=latitude + radius,
            longitude__gte=longitude - radius,
            longitude__lte=longitude + radius
        )

        serializer = DriverLocationSerializer(nearby_drivers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class TravellerHistoryView(APIView):
    def get(self, request):
        # Authenticate the user
        user = authenticate_token(request)

        # Get the passenger instance associated with the authenticated user
        passenger = get_object_or_404(Passenger, user=user)

        # Fetch the rides history for the authenticated passenger
        rides = TravelHistory.objects.filter(passenger=passenger)
        
        # Serialize the rides data
        serializer = TravelHistorySerializer(rides, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
