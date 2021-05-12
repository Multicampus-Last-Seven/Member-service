from django.urls import path
from . import views

urlpatterns = [
    path('serials', views.serialsList, name='serials'),
    path('signup', views.signup, name='signup'),
    path('email-check', views.check_email, name='email_check'),
    path('userid-check', views.check_userid, name='userid_check'),
    path('login', views.login, name='login'),
    path('<str:pk1>/<str:pk2>', views.register_serial, name='serial_registraion')
]
