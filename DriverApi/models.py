from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models import DecimalField
from django.contrib.auth.models import User


class DriverManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)

class Driver(AbstractBaseUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE,default="1")
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    number = models.IntegerField(unique=True)
    auto_no = models.CharField(max_length=80, unique=True, null=False, blank=False)
    
    # Add these required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'number', 'auto_no']
    
    objects = DriverManager()
    
    def save(self, *args, **kwargs):
        if not self.pk or self.password != Driver.objects.get(pk=self.pk).password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    def check_password(self, password):
        return check_password(password, self.password)
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.auto_no})"
class DriverLocation(models.Model):
    """
    Stores auto drivers' locations when the driver is logged into the application.
    """
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    latitude = DecimalField(max_digits=9, decimal_places=6)
    longitude = DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"{self.driver} - Location: ({self.latitude}, {self.longitude})"

class DriverRidesHistory(models.Model):
    """
    Stores ride history for auto drivers.
    """
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    passenger = models.ForeignKey('PassengerApi.Passenger', on_delete=models.CASCADE)
    source_address = models.TextField()
    destination_address = models.TextField()
    booked_time = models.DateTimeField(auto_now_add=True)
    auto_no = models.CharField(max_length=80)
    passenger_name = models.CharField(max_length=80)

    def __str__(self):
        return f"Ride: {self.passenger_name} by {self.driver} from {self.source_address} to {self.destination_address}"

from django.db import models
from django.db.models import Min

class CurrentBooking(models.Model):
    """
    Stores current bookings for drivers, which can later be moved to ride history.
    """
    id = models.IntegerField(primary_key=True, editable=False)  # Set primary key explicitly
    passenger = models.ForeignKey('PassengerApi.Passenger', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    source_address = models.TextField()
    destination_address = models.TextField()
    booked_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.id:  # Only set id if it's a new record
            # Find the smallest available ID starting from 1
            all_ids = CurrentBooking.objects.values_list('id', flat=True)
            for potential_id in range(1, len(all_ids) + 2):
                if potential_id not in all_ids:
                    self.id = potential_id
                    break

        super(CurrentBooking, self).save(*args, **kwargs)

    def __str__(self):
        return f"Current Booking for {self.passenger} with {self.driver}"
