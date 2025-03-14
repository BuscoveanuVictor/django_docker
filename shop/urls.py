from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.ShopView, name='shop'),
    path('contact/', views.contact, name='contact'),
    path('product/<int:instrument_id>/', views.productView, name='productView'),
    path('add_instrument/', views.add_instrument, name='add_instrument'),
]

