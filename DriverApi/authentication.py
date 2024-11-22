# authentication.py

from django.contrib.auth.backends import ModelBackend
from .models import Driver

class DriverAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            driver = Driver.objects.get(email=email)
            if driver.check_password(password):
                return driver
        except Driver.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return Driver.objects.get(pk=user_id)
        except Driver.DoesNotExist:
            return None