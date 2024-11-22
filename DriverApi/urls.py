from django.urls import path
from .views import (
    SignupDriver,
    LoginDriver,
    LogoutDriver,
    UpdateDriverLocation,
    DriverRidesHistoryView,
    CompleteRide,
    CurrentBookedRide,
    CancelRide
)

urlpatterns = [
    path('signup/', SignupDriver.as_view(), name='signup_driver'),
    path('login/', LoginDriver.as_view(), name='login_driver'),
    path('logout/', LogoutDriver.as_view(), name='logout_driver'),
    path('update-location/', UpdateDriverLocation.as_view(), name='update_driver_location'),
    path('rides-history/', DriverRidesHistoryView.as_view(), name='driver_rides_history'),
    path('complete-ride/', CompleteRide.as_view(), name='complete_ride'),
    path('current-booked-ride/', CurrentBookedRide.as_view(), name='current-booked-ride'),
    path('Cancel-ride/', CancelRide.as_view(), name='Cancel-Ride'),

]
