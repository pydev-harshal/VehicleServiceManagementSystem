from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from Users.models import Servicing
from django.contrib.auth.hashers import make_password
from Users.models import Users
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

# Create your models here.
NOTIFICATION_STATUS_CHOICES = [
    ('Booking Confirmed', 'Booking Confirmed'),
    ('On Going', 'On Going'),
    ('Completed', 'Completed'),
    ('Delivered', 'Delivered'),
]

def send_creds_to_admin(message,recipient):
    subject = f'MOTORA'

    from_email = settings.EMAIL_HOST_USER

    
    send_mail(subject, message, from_email, [recipient])

class CreateAdmin(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    first_name = models.CharField(max_length=100, blank=True,null=True)
    last_name = models.CharField(max_length=100, blank=True,null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True,unique=True)

    def save(self, *args, **kwargs):
        try:
            Users.objects.get(email=self.email)
            raise ValidationError("Email Already Exists")

        except:

            obj = Users.objects.create(username=self.email,password=make_password(self.password),email=self.email,
                                    first_name=self.first_name,last_name=self.last_name,role="Admin",status="In Active")
            
            raw_password = self.password

            if self.password and not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2')):
                self.password = make_password(self.password)
            self.user_id = obj
            
            message = f'''
            VSMS Access Credentials
            Name: {self.first_name} {self.last_name}
            Email: {self.email}
            password: {raw_password}
            '''
            send_creds_to_admin(message,self.email)

        super().save(*args, **kwargs)


class Notification(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True,blank=True)
    service_id = models.ForeignKey(Servicing,on_delete=models.CASCADE)
    status = models.CharField(max_length=100,choices=NOTIFICATION_STATUS_CHOICES,default="Booking Confirmed")
    created_on = models.DateTimeField(auto_now_add=True)

        


            


