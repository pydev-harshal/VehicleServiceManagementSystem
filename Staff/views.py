from django.shortcuts import render,redirect
from django.urls import reverse
from Users.models import Users ,Servicing,Enquiry
from Staff.models import Notification
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from Users.mail import send_mail_to_the_user , create_notification
from Staff.decorators import staff_custom_login_required
import json
# Create your views here.
from datetime import datetime
from django.utils.timesince import timesince
from django.utils import timezone
def format_time_difference(time_difference):
    # Example time difference string: '20 hours, 38 minutes'
    time_parts = time_difference.split(', ')

    formatted_time = ''
    for part in time_parts:
        if 'hour' in part:
            hours = part.split()[0]
            formatted_time += f'{hours}H,'
        elif 'minute' in part:
            minutes = part.split()[0]
            formatted_time += f'{minutes}M'

    return formatted_time + ' ago'
def calculate_time_difference(notifications):
    current_time = timezone.localtime(timezone.now())  # Get current time in the current timezone

    for notification in notifications:
        # Convert created_on to timezone-aware datetime
        created_on_aware = timezone.localtime(notification.created_on)

        # Calculate the time difference
        time_difference = current_time - created_on_aware

        # Convert time difference to a human-readable format
        time_ago = timesince(created_on_aware)

        # Add a temporary attribute to each Notification object to hold the time difference
        notification.time_ago = format_time_difference(time_ago)





def get_staff_data():
    services = Servicing.objects.all()
    pending = services.filter(admin_remark = "Pending")
    on_going = services.filter(admin_remark = "On Going")
    delivered = services.filter(admin_remark = "Delivered")
    completed = services.filter(admin_remark = "Completed")
    total = len(pending) + len(delivered) + len(on_going) + len(completed)
    all = len(pending) + len(completed) + len(on_going)
    data = {'pending': len(pending), 'on_going': len(on_going), 'delivered':len(delivered),'all': all,'total': total,'completed':len(completed)}

    enq = Enquiry.objects.all()
    data['all_enq'] = len(enq)
    data['active_enq'] = len(enq.filter(status = "Active"))
    data['handled_enq'] = len(enq.filter(status = "Handled"))

    return data


def index_data():
    services = Servicing.objects.all()
    total_amount = sum([int(x['total_amount']) for x in services.values('total_amount')])
    print(total_amount)
    delivered_request = Servicing.objects.filter(admin_remark = "Delivered").all().count()
    total_users = Users.objects.filter(status = 'Active').all().count()

    two = services.filter(category = "2 Wheeler").count()
    four = services.filter(category = "4 Wheeler").count()

    two2 = sum([int(x['total_amount']) for x in services.filter(category = "2 Wheeler").values('total_amount')])
    four4 = sum([int(x['total_amount']) for x in services.filter(category = "4 Wheeler").values('total_amount')])
    two_four = [four4,two2]
    values = [two, four]
    print(four4,two2,)
    print(values)

    notifications = Notification.objects.all().order_by('-created_on')
    calculate_time_difference(notifications)


    s_c = [int(x['service_charge']) for x in services.values('service_charge')]
    p_c = [int(x['parts_charge']) for x in services.values('parts_charge')]
    o_c = [int(x['other_charge']) for x in services.values('other_charge')]
    

    return {'total_amount': total_amount,'delivered_request': delivered_request,'total_users': total_users,'two': two,'four': four,'values': values,'services':services,'notifications':notifications,
            'two2':two2,'four4':four4,'two_four':two_four,'o_c':o_c,'p_c':p_c,'o_c':o_c}





def staff_index(request):
    if request.user.is_authenticated:
        return render(request,'staff-index.html',context={'data':get_staff_data(),'index_data':index_data()})
    else:
        return redirect('staff-login')
def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request,email=email, password=password)
        if user:
            if user.role == "User":
                messages.add_message(request, messages.ERROR, "Access Denied")
                return redirect (reverse('staff-login'))
            else:
                login(request,user)
                return redirect('staff-index')
        else:
            messages.add_message(request, messages.ERROR, "Email or Password not Matching")
            return redirect (reverse('staff-login'))
    else:
        return render(request,'staff-login.html')
    
def staff_logout(request):
    logout(request)
    return redirect('staff-index')

@staff_custom_login_required
def staff_profile(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'update':
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            try:
                first,last = str(full_name).split()
            except:
                first = str(full_name).capitalize()
                last = ""


            if str(email).lower() == request.user.email:
                user_profile = Users.objects.get(id = int(request.user.id))
                user_profile.first_name = first.capitalize()
                user_profile.last_name = last.capitalize()
                user_profile.save()
                messages.add_message(request, messages.INFO, "Update Success")
                return redirect('staff-profile')

            if Users.objects.filter(email=str(email).lower()).exists():
                messages.add_message(request, messages.ERROR, "Cannot Update :Email Already Taken")
                return redirect(reverse('staff-profile'))
            else:
                user = Users.objects.get(id = int(request.user.id))
                user.email = str(email).lower()
                user.first_name =first.capitalize()
                user.last_name =last.capitalize()
                user.save()
                messages.add_message(request, messages.INFO, "Update Success")
                return redirect('staff-profile')
        else:
            old_password = request.POST.get('old_password')
            newpassword = request.POST.get('newpassword')
            renewpassword = request.POST.get('renewpassword')
            user = authenticate(email = request.user.email ,password = old_password)
            if user:
                if newpassword == renewpassword:
                    user.set_password(newpassword)
                    user.save()
                    messages.add_message(request, messages.INFO, "Password Updated")
                    login(request,user)
                    return redirect('staff-profile')
                else:        
                    messages.add_message(request, messages.ERROR, "Password Not Matching")
                    return redirect('staff-profile')

            else:
                messages.add_message(request, messages.ERROR, "Current Password Invalid")
                return redirect('staff-profile')
    else:
        return render(request,'staff-profile.html',context={'data':get_staff_data()})

@staff_custom_login_required
def service_requests(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        obj = Servicing.objects.get(id=id)
        obj.admin_remark = "On Going"
        obj.save()
        message = f"""
        Work-In Progress for
        Vehicle No.:{obj.vehicle_reg_no} Comfirmed.
        Service Number : {obj.service_number}
        Date : {obj.service_date}
        Time : {str(obj.service_time).upper()}

        MOTORA    
        """
        create_notification(obj.profile_id.user_id,obj,"On Going")
        send_mail_to_the_user(message,obj.profile_id.user_id.email)
        return redirect('service-requests')
    else:
        services = Servicing.objects.filter(admin_remark="Pending").all()
        return render(request,'service-requests.html',context={'services':services,'data':get_staff_data()})

@staff_custom_login_required
def enquiry_list(request):
    if request.method == 'POST':
        obj = Enquiry.objects.get(id=request.POST.get('id'))
        if obj.status == "Active":
            obj.status = "Handled"
        else:
            obj.status = "Active"
        obj.save()
        return redirect('enquiry-list')

    else:
        enquires = Enquiry.objects.filter(status="Active").all()
        return render(request,'enquiry-list.html',context={'enquires':enquires,'data':get_staff_data()})

@staff_custom_login_required
def handled_enquiry_list(request):
    if request.method == 'POST':
        obj = Enquiry.objects.get(id=request.POST.get('id'))
        if obj.status == "Active":
            obj.status = "Handled"
        else:
            obj.status = "Active"
        obj.save()
        return redirect('handled_enquiry-list')

    else:
        enquires = Enquiry.objects.filter(status="Handled").all()
        return render(request,'handled_enquiry-list.html',context={'enquires':enquires,'data':get_staff_data()})

@staff_custom_login_required
def on_going_request(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'status':
            id = request.POST.get('id')
            obj = Servicing.objects.get(id=id)
            obj.admin_remark = "Completed"
            obj.save()
            message = f"""
            Work Completed for
            Vehicle No :{obj.vehicle_reg_no}.
            Service Number : {obj.service_number}
            Amount : {obj.total_amount} $

            MOTORA    
            """
            create_notification(obj.profile_id.user_id,obj,"Completed")
            send_mail_to_the_user(message,obj.profile_id.user_id.email)
            return redirect('on_going-request')
        else:
            id = request.POST.get('id')
            obj = Servicing.objects.get(id=id)
            obj.service_charge = obj.service_charge + int(request.POST.get('service_charge',int(0))) if request.POST.get('service_charge') != '' else 0
            obj.other_charge = obj.other_charge + int(request.POST.get('other_charge',int(0))) if request.POST.get('other_charge') != '' else 0
            obj.parts_charge = obj.parts_charge + int(request.POST.get('parts_charge',int(0))) if request.POST.get('parts_charge') != '' else 0
            obj.total_amount= obj.total_amount+float(obj.service_charge+obj.other_charge+obj.parts_charge)
            obj.save()
            return redirect('on_going-request')
    else:
        services = Servicing.objects.filter(admin_remark="On Going").all()
        return render(request,'on_going-requests.html',context={'services':services,'data':get_staff_data()})
    

@staff_custom_login_required
def completed_request(request):
    if request.method == 'POST':
        if request.POST.get('action') =='status':
            id = request.POST.get('id')
            obj = Servicing.objects.get(id=id)
            obj.admin_remark = "Delivered"
            message = f"""
            Vehicle No.:{obj.vehicle_reg_no} Delivered.
            Service Number : {obj.service_number}

            Thank You for choosing us....            
            MOTORA    
            """
            create_notification(obj.profile_id.user_id,obj,"Delivered")
            send_mail_to_the_user(message,obj.profile_id.user_id.email)
            obj.save()
            return redirect('completed-request')
        elif request.POST.get('action') =='deliver':
            id = request.POST.get('id')
            obj = Servicing.objects.get(id=id)
            obj.payment_status = True
            obj.save()
            create_notification(obj.profile_id.user_id,obj,"Payment Confirmed")
            return redirect('user-service')
        else:
            id = request.POST.get('id')
            obj = Servicing.objects.get(id=id)
            obj.payment_status = True
            obj.save()
            message = f"""
            Payment Confirmed
            Vehicle No.:{obj.vehicle_reg_no}.
            Service Number : {obj.service_number}
            Date : {obj.service_date}

            Amount : {obj.total_amount} $

            Thank You for choosing us....            
            MOTORA    
            """
            create_notification(obj.profile_id.user_id,obj,"Payment Completed")
            send_mail_to_the_user(message,obj.profile_id.user_id.email)
            return redirect('completed-request')
    else:
        services = Servicing.objects.filter(admin_remark="Completed").all()
        return render(request,'completed-requests.html',context={'services':services,'data':get_staff_data()})
    
@staff_custom_login_required
def delivered_request(request):
    services = Servicing.objects.filter(admin_remark="Delivered").all()
    return render(request,'delivered-requests.html',context={'services':services,'data':get_staff_data()})


def all_request(request):
    services = Servicing.objects.all()
    return render(request,'all-request.html',context={'services':services,'data':get_staff_data()})