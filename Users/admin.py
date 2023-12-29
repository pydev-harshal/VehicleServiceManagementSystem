from django.contrib import admin
from Users.models import *
# Register your models here.

# admin.site.register(Users)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id','full_name','phone_number')
admin.site.register(UserProfile,UserProfileAdmin)

class ServicingAdmin(admin.ModelAdmin):
    list_display = ('id','service_number','category','vehicle_reg_no','admin_remark')
admin.site.register(Servicing,ServicingAdmin)



class UsersAdmin(admin.ModelAdmin):
    list_display = ('id','email','role','status')
admin.site.register(Users,UsersAdmin)


class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('id','full_name','email','contact_number','message','enquiry_from','status')
admin.site.register(Enquiry,EnquiryAdmin)