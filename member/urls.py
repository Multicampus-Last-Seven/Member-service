from django.urls import path
from . import views

urlpatterns = [
    path('find/password', views.find_password, name='find_password'),
    path('find/userid', views.find_userid, name='find_userid'),
    path('serials', views.serialsList, name='serials'),
    path('signup', views.signup, name='signup'),
    path('email-check', views.check_email, name='email_check'),
    path('userid-check', views.check_userid, name='userid_check'),
    path('login', views.login, name='login'),
    path('activate/<str:userid>/<str:token>', views.activate, name='activate'),
    path('<str:userid>', views.update_user, name='update_user'),
    path('<str:userid>/<str:serialid>', views.serial_view, name='serial_view'),
    path('<str:serialid>', views.serial_alive_view, name='serial_alive_view')  
]
