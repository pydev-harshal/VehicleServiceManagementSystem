from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from Staff.models import Notification


def send_mail_to_the_user(message,recipient):
    subject = f'MOTORA'

    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [recipient])


def send_sms(message,phone_number):
    account_sid = 'ACb2645f4649874949a12ba4243466cb60'
    auth_token = '11f84be731da3bee3265fb6011a66e70'
    # Your Twilio phone number
    twilio_phone_number = '+12817308928'
    recipient_phone_number = '+91' + str(phone_number)  # Replace with the phone number you want to send the SMS to

# Your message
    message_body = message

    # Initialize Twilio client
    client = Client(account_sid, auth_token)

    # Send SMS
    message = client.messages.create(
        body=message_body,
        from_=twilio_phone_number,
        to=recipient_phone_number
    )

    print(f"Message SID: {message.sid}")


def create_notification(user,service, status):
    notification = Notification.objects.create(user_id = user,
        service_id = service , status = status
    )
    notification.save()