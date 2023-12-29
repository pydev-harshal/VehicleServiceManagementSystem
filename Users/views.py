from django.shortcuts import render,redirect
from django.urls import reverse
from Users.models import *
from Staff.models import *
from django.contrib import messages
from Users.mail import send_mail_to_the_user , send_sms , create_notification
import phonenumbers
from django.contrib.auth import authenticate, login, logout
from django.forms.models import model_to_dict
from Staff.decorators import user_custom_login_required
# Create your views here.


def get_user_profile(request):

        notifications = Notification.objects.filter(user_id = request.user.id).order_by('-created_on')
        user_profile = UserProfile.objects.get(user_id = int(request.user.id))
        user_profile_dict = model_to_dict(user_profile)
        try:
            first,last = user_profile_dict['full_name'].split()
        except:
            first = str(user_profile_dict['full_name'])
            last = ""
        return {'user_profile':user_profile,'first':first,'last':last,'notifications':notifications}

def format_license_plate(input_string):
    if len(input_string) != 10:
        return "Invalid input: Input length should be 10 characters."

    # Check if the input is already in the desired format
    expected_format = input_string[:2].upper() + " " + input_string[2:4].upper() + " " + input_string[4:6].upper() + " " + input_string[6:]
    if input_string == expected_format:
        return input_string  # Return the input as it's already in the correct format

    # If not in the correct format, perform the transformation
    first_part = input_string[:2].upper()
    second_part = input_string[2:4].upper()
    third_part = input_string[4:6].upper()
    last_part = input_string[6:]

    formatted_string = f"{first_part} {second_part} {third_part} {last_part}"
    return formatted_string

#Landing Page and Enquiry Form
def index(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            contact_number = request.POST.get('phone_number')
            message = request.POST.get('message')

            Enquiry.objects.create(full_name = str(full_name).title() , email = str(email).lower() , contact_number = contact_number , message = message)
            try:
                Users.objects.get(email = str(email).lower())
            except:
                Users.objects.create(email = str(email).lower() , username = str(email).lower())

            message = f"""
            Hello {str(full_name).title()}
            Thank You for Contacting MOTORA, Customer support team will contact you shortly. Thank you!
            MOTORA    
            """
            send_mail_to_the_user(message,email)
            messages.add_message(request, messages.INFO, "Support team will contact you shortly. Thank you!")
            return redirect (reverse('index') + '#contact')
        
        except Exception as e:
            messages.add_message(request, messages.ERROR, f"Something Went Wrong")
            return redirect (reverse('index') + '#contact')
    else:
        return render(request,'webapp/index.html')
    

@user_custom_login_required
def user_index(request):
    return render(request,'user-index.html',context=get_user_profile(request))



def user_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = str(full_name).title()
        email = str(email).lower()

        parsed_number = phonenumbers.parse(phone_number, 'IN')
        is_valid = phonenumbers.is_valid_number(parsed_number)

        if not is_valid:
            messages.add_message(request, messages.ERROR, "Phone Number Invalid")
            return redirect (reverse('user-register'))
            
        if password == confirm_password:
            user = Users.objects.filter(email=str(email).lower()).first()
            if user:
                if UserProfile.objects.filter(user_id = user.id).exists():
                    messages.add_message(request, messages.WARNING, "Email Already Exists")
                    return redirect (reverse('user-register'))
                else:
                    p_id = UserProfile.objects.create(user_id=user, full_name=full_name, phone_number = phone_number)
                    user.set_password(password)
                    user.status = "Active"
                    user.save()
                    message = f"""
                    Welcome {str(full_name).capitalize()}:
                    Thank You for Registering MOTORA.
                    MOTORA    
                    """
                    send_mail_to_the_user(message,email)
            else:
                user = Users.objects.create(email = str(email).lower() , username = str(email).lower())
                UserProfile.objects.create(user_id=user, full_name=full_name, phone_number = phone_number)
                user.set_password(password)
                user.status = "Active"
                user.save()
                message = f"""
                Welcome {str(full_name).capitalize()}:
                Thank You for Registering with MOTORA.
                MOTORA    
                """
                send_mail_to_the_user(message,email)
            return redirect('user-login')
        else:
            messages.add_message(request, messages.INFO, "Password Not Matching")
            return redirect (reverse('user-register') + '#yourConfirmPassword')
    else:
        return render(request,'user-register.html')
    

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=str(email).lower(), password=password)
        if user:
            login(request,user)
            return redirect('user-index')
        else:
            messages.add_message(request, messages.ERROR, "Email or Password not Matching")
            return redirect (reverse('user-login'))
    else:
        return render(request,'user-login.html')
    

def user_logout(request):
    logout(request)
    return redirect('index')



@user_custom_login_required
def user_profile(request):
    if request.method == 'POST':

        if request.POST.get('form_type') == 'update':
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            email = request.POST.get('email')

            if str(email).lower() == request.user.email:
                user_profile = UserProfile.objects.get(user_id = int(request.user.id))
                user_profile.full_name = full_name
                user_profile.phone_number = phone_number
                user_profile.save()
                message = f"""
                Hello {str(full_name)}
                Your Profile has been Updated Successfully !
                """
                send_mail_to_the_user(message,request.user.email)
                messages.add_message(request, messages.INFO, "Profile Updated Successfully")
                return redirect('user-profile')

            if Users.objects.filter(email=str(email).lower()).exists():
                messages.add_message(request, messages.ERROR, "Cannot Update :Email Already Taken")
                return redirect(reverse('user-profile'))
            else:
                user = Users.objects.get(id = int(request.user.id))
                user.email = str(email).lower()
                user.save()
                user_profile = UserProfile.objects.get(user_id = int(request.user.id))
                user_profile.full_name = full_name
                user_profile.phone_number = phone_number
                user_profile.save()
                message = f"""
                Hello {str(full_name)}
                Your Profile has been Updated Successfully !
                """
                # send_sms(message,str(phone_number))
                send_mail_to_the_user(message,request.user.email)
                messages.add_message(request, messages.INFO, "Profile Updated Successfully")
                return redirect('user-profile')
        else:
            old_password = request.POST.get('old_password')
            newpassword = request.POST.get('newpassword')
            renewpassword = request.POST.get('renewpassword')
            user = authenticate(email = request.user.email ,password = old_password)
            if user:
                if newpassword == renewpassword:
                    user.set_password(newpassword)
                    user.save()
                    login(request,user)
                    user_name = UserProfile.objects.filter(user_id = user.id).values('full_name').first()
                    message = f"""
                    Hello {str(user_name['full_name'])}
                    Your Password Changed Successfully !
                    """
                    send_mail_to_the_user(message,request.user.email)
                    messages.add_message(request, messages.INFO, "Password Updated Successfully")
                    return redirect('user-profile')
                else:        
                    messages.add_message(request, messages.ERROR, "Password Not Matching")
                    return redirect('user-profile')
            else:
                messages.add_message(request, messages.ERROR, "Current Password Invalid")
                return redirect('user-profile')
    else:
        return render(request,'user-profile.html',context=get_user_profile(request))




@user_custom_login_required
def user_contact(request):
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            message = request.POST.get('message')

            Enquiry.objects.create(full_name = str(full_name).title() , email = str(email).lower() , contact_number = contact_number , message = message,enquiry_from="Dashboard")
            try:
                Users.objects.get(email = str(email).lower())
            except:
                Users.objects.create(email = str(email).lower() , username = str(email).lower())
            amessages = f"""
            Hello {str(full_name).title()} Thank You for Contacting MOTORA ,
            Customer support team, 
            will contact you shortly. Thank you!

            MOTORA    
            """
            send_mail_to_the_user(amessages,email)
            messages.add_message(request, messages.INFO, "Our Team will contact you soon.....")
            return redirect (reverse('user-contact'))
        
        except Exception as e:

            messages.add_message(request, messages.ERROR, f"Something Went Wrong: {e}")
            print(e)
            return redirect (reverse('user-contact'))
        
    else:
        return render(request,'user-contact.html',context=get_user_profile(request))
    
@user_custom_login_required
def user_book_service(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        vehicle_reg_no = request.POST.get('vehicle_reg_no')
        vehicle_name = request.POST.get('vehicle_name')
        vehicle_brand = request.POST.get('vehicle_brand')
        vehicle_model = request.POST.get('vehicle_model')
        service_date = request.POST.get('service_date')
        service_time = request.POST.get('service_time')
        pickup_address = request.POST.get('pickup_address')
        need_delivery = True
        
        if len(str(vehicle_reg_no)) != 10:
            messages.add_message(request, messages.ERROR, "Invalid Vehicle Registration Number")
            return redirect('user-book-service')
        
        vehicle_reg_no = format_license_plate(str(vehicle_reg_no))

        if request.POST.get('need_delivery') == None:
            need_delivery = False
        p_id = UserProfile.objects.get(user_id=int(request.user.id))
        s_id = Servicing.objects.create(profile_id=p_id,vehicle_reg_no=vehicle_reg_no.upper(),category=category,vehicle_name=vehicle_name,vehicle_brand=vehicle_brand,vehicle_model=vehicle_model,service_date=service_date,service_time=service_time,pickup_address=pickup_address.title(),need_delivery=need_delivery)
        message = f"""
        Service Request for Vehicle No.:{s_id.vehicle_reg_no} Comfirmed.
        Service Number : {s_id.service_number}
        Date : {s_id.service_date}
        Time : {str(s_id.service_time).upper()}

        MOTORA    
        """
        # send_sms(message,str(p_id.phone_number))
        send_mail_to_the_user(message,request.user.email)
        create_notification(request.user,s_id,'Booking Confirmed')
        return redirect('user-service')
    else:
        return render(request,'user-book-service.html',context=get_user_profile(request))
    
@user_custom_login_required
def user_service(request):
    services = Servicing.objects.filter(profile_id = UserProfile.objects.get(user_id=request.user.id)).exclude(admin_remark = "Delivered").all()
    context = get_user_profile(request)
    context['services'] = services
    return render(request,'user-service.html',context=context)


@user_custom_login_required
def user_delivered_service(request):
    services = Servicing.objects.filter(profile_id = UserProfile.objects.get(user_id=request.user.id)).filter(admin_remark = "Delivered").all()
    context = get_user_profile(request)
    context['services'] = services
    return render(request,'user-delivered-service.html',context=context)