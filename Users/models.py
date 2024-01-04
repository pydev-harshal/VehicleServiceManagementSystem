from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
import random
from django.contrib.auth.hashers import make_password
# Create your models here.

USER_ROLES = [
    ('Admin', 'Admin'),
    ('User', 'User'),
]

ENQUIRY_STATUS = [
    ('Active', 'Active'),
    ('Handled', 'Handled')
]

USER_STATUS = [
    ('Active' , 'Active'),
    ('In Active' , 'In Active')
]

CATEGORY_CHOICES = [
    ('2 Wheeler','2 Wheeler'),
    ('4 Wheeler','4 Wheeler'),
    ('Bus','Bus'),
    ('Truck','Truck')
]

ADMIN_REMARK_CHOICES = [
    ("Pending","Pending"),
    ("On Going","On Going"),
    ("Completed","Completed"),
    ("Delivered","Delivered")
]

def generate_unique_number():
        while True:
            # Generate a random 9-digit number
            new_number = random.randint(100000000, 999999999)
            try:
                # Check if the generated number already exists
                Servicing.objects.get(service_number=new_number)
            except:
                # If the number doesn't exist, return it
                return new_number


class Users(AbstractUser):
    email = models.EmailField(unique=True,null=True,blank=True)
    role = models.CharField(max_length=10, default='User', choices=USER_ROLES, null=True)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=9, default='In Active', choices=USER_STATUS, null=True)

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['username']


    
    def save(self, *args, **kwargs):
   
        if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
        
            self.password = make_password(self.password)
        
        super().save(*args, **kwargs)


class Enquiry(models.Model):
    full_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=False,null=True,blank=True)
    contact_number = PhoneNumberField(null=True, blank=True, unique=False)
    message = models.TextField(null=True,blank=True)
    enquiry_from = models.CharField(max_length=10,null=True,blank=True,default="Website")
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=10,choices=ENQUIRY_STATUS,null=True,blank=True,default="Active")


class UserProfile(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    phone_number = PhoneNumberField(null=True, blank=True, unique=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    

class Servicing(models.Model):

    profile_id = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    
    service_number = models.IntegerField(default=generate_unique_number,unique=True)
    service_request_date = models.DateTimeField(auto_now_add=True)

    category = models.CharField(max_length=100,choices=CATEGORY_CHOICES,null=True,blank=True)
    vehicle_name = models.CharField(max_length=100,null=True,blank=True)
    vehicle_brand = models.CharField(max_length=100,null=True,blank=True)
    vehicle_model = models.CharField(max_length=100,null=True,blank=True)
    vehicle_reg_no = models.CharField(max_length=100,null=True,blank=True)
    service_time = models.TimeField(null=True,blank=True)
    service_date = models.DateField(null=True,blank=True)

    pickup_address = models.CharField(max_length=100,null=True,blank=True)
    need_delivery = models.BooleanField(default=False,null=True,blank=True)

    service_charge = models.IntegerField(null=True,blank=True,default=0)
    other_charge = models.IntegerField(null=True,blank=True,default=0)
    parts_charge = models.IntegerField(null=True,blank=True,default=0)
    total_amount = models.IntegerField(null=True,blank=True,default=0)

    payment_status = models.BooleanField(default=False)

    admin_remark = models.CharField(max_length=100,null=True,blank=True,choices=ADMIN_REMARK_CHOICES,default="Pending")


