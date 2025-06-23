from django.urls import path
from . import views

urlpatterns = [
  path('cargarapi/', views.guardar_api_validacion, name='cargarapi'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cargar-pedidos/', views.cargar_pedidos, name='cargarpedidos'), 
    path('logout/',views.logout_view, name='logout'),
    path('pedidos/', views.org_pedidos, name='pedidos'),
    path('map/',views.ver_mapa,name='mapa'),
]
