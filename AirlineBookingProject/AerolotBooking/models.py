from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager

# Create your models here.
class Flight(models.Model):
    flight_id = models.IntegerField(primary_key=True)
    flight_code=models.CharField(max_length=10)
    origin=models.CharField(max_length=3)
    destination=models.CharField(max_length=3)
    departure_time=models.DateTimeField()
    arrival_time=models.DateTimeField()
    price=models.DecimalField(decimal_places=2,max_digits=10)
    duration=models.CharField(max_length=10)
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    objects = CustomUserManager()
    username = None
    email = models.EmailField('email address', unique=True)
    email_verified = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    flight_id=models.ForeignKey(Flight, on_delete=models.CASCADE)
    passanger_number=models.IntegerField(null=True)
    passengers = models.JSONField(default=dict)
    booking_date=models.DateTimeField()
class Ad(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_title=models.CharField(max_length=40)
    ad_content=models.TextField()
    ad_img=models.CharField(max_length=40)





