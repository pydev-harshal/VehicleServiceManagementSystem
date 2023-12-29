from django.urls import path
from Users.views import *


urlpatterns = [
    path('',index,name="index"),
    path('user-index/',user_index,name="user-index"),

    path('user-register/',user_register,name="user-register"),
    path('user-login/',user_login,name="user-login"),
    path('user-logout/',user_logout,name="user-logout"), 
    
    path('user-profile/',user_profile,name="user-profile"),
    path('user-contact/',user_contact,name="user-contact"),

    path('user-book-service/',user_book_service,name="user-book-service"),
    path('user-service/',user_service,name="user-service"),
    path('user-delivered-service/',user_delivered_service,name="user-delivered-service"),
]
