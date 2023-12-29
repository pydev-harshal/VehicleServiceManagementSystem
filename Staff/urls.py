from django.urls import path
from Staff.views import *

urlpatterns = [
    path('',staff_index,name="staff-index"),
    path('staff-profile',staff_profile,name="staff-profile"),
    path('login/',staff_login,name="staff-login"),
    path('logout/',staff_logout,name="staff-logout"),
    path('service-requests/',service_requests,name="service-requests"),
    path('on_going-request/',on_going_request,name="on_going-request"),
    path('enquiry-list/',enquiry_list,name="enquiry-list"),
    path('handled_enquiry-list/',handled_enquiry_list,name="handled_enquiry-list"),
    path('handled_enquiry-list/',handled_enquiry_list,name="handled_enquiry-list"),
    path('completed-request/',completed_request,name="completed-request"),
    path('delivered-request/',delivered_request,name="delivered-request"),
    path('all_request/',all_request,name="all_request"),
]
