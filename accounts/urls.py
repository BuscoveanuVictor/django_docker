from django.urls import path
from .views import  index_view, register_view, confirm_mail_view, login_view, logout_view, profile_view, password_change_view

urlpatterns = [
    path('', index_view, name='index'),
    path('register/', register_view, name='register'),
    path('confirm-email/<str:code>/', confirm_mail_view, name='confirm_email'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('password-change/', password_change_view, name='password_change'),
]