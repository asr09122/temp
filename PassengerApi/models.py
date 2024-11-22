from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

class Passenger(models.Model):
    """
    Stores passenger info for campus students.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE,default="1")
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField()
    password = models.CharField(max_length=200)
    number = models.IntegerField(unique=True)
    roll_no = models.CharField(max_length=20, unique=True)
    subgroup_year = models.CharField(max_length=10)  # e.g., "2024", "2025"


    def save(self, *args, **kwargs):
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, password):
        return check_password(password, self.password)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_no})"

class TravelHistory(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    driver = models.ForeignKey('DriverApi.Driver', on_delete=models.CASCADE)
    source_address = models.TextField()
    destination_address = models.TextField()
    booked_time = models.DateTimeField(auto_now_add=True)
    auto_no = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.passenger} -> {self.driver} | {self.booked_time}"
