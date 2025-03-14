from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_list, name='cart_list'),
    path('process-order/', views.process_order, name='process_order'),
]


