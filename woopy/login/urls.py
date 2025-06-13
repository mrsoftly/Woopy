from django.urls import path
from . import views

urlpatterns = [
    path('', views.log, name='login'),  # Ruta para la vista de login
]