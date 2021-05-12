from django.urls import path
from . import views

urlpatterns = [
    path('serials', views.serialsList, name='serials'),
    path('signup', views.signup, name='signup'),
    path('email-check', views.check_email, name='email_check'),
    path('login', views.login, name='login')
]
