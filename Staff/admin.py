from django.contrib import admin
from Staff.models import *
from Users.models import *
# Register your models here.



class CreateAdminAdmin(admin.ModelAdmin):
    list_display = ('id','email', 'first_name', 'last_name')

admin.site.register(CreateAdmin,CreateAdminAdmin)