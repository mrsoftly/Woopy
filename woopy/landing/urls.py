from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('planes/',views.prices,name='prices'),
    path('contactanos/',views.contact,name='form'),  
]
