from django.urls import path
from .views import (
    SignupPassenger,
    LoginPassenger,
    LogoutPassenger,
    BookRide,
    CancelRide,
    FindNearbyDrivers,
    TravellerHistoryView
)

urlpatterns = [
    path('signup/', SignupPassenger.as_view(), name='signup_passenger'),
    path('login/', LoginPassenger.as_view(), name='login_passenger'),
    path('logout/', LogoutPassenger.as_view(), name='logout_passenger'),
    path('book-ride/', BookRide.as_view(), name='book_ride'),
    path('cancel-ride/', CancelRide.as_view(), name='cancel_ride'),
    path('nearby-drivers/', FindNearbyDrivers.as_view(), name='find_nearby_drivers'),  # New endpoint for finding nearby drivers
    path('history/', TravellerHistoryView.as_view(), name='history'),  # New endpoint for finding nearby drivers
]
