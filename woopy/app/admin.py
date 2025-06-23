from django.contrib import admin
from .models import Plan, ApiWoo,Pedido,PedidoOrdenado

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'duracion', 'max_envios_diarios']
    list_filter = ['duracion']
    search_fields = ['nombre']
    ordering = ['precio']
@admin.register(ApiWoo)
class ApiWooAdmin(admin.ModelAdmin):
    list_display = ['user', 'url', 'consumer_key']  # quitar 'created_at'
    search_fields = ['user__username', 'url', 'consumer_key']
    list_filter = ['user']
    ordering = ['user']
   
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = [
        'num_pedido', 'user', 'nombre_cliente', 'estado_pedido', 'fecha_pedido'
    ]
    search_fields = [
        'num_pedido', 'user__username', 'nombre_cliente', 'estado_pedido', 'comuna', 'region'
    ]
    list_filter = [
        'estado_pedido', 'fecha_pedido', 'user'
    ]
    ordering = ['-fecha_pedido']

    # Opcional: campos de solo lectura
    readonly_fields = ['latitud', 'longitud']  
@admin.register(PedidoOrdenado)
class PedidoOrdenadoAdmin(admin.ModelAdmin):
    list_display = [
         'user', 'pedido', 'latitud', 'longitud'
    ]
    search_fields = [
        'user', 'pedido', 'latitud', 'longitud'
    ]
    list_filter = [
         'user'
    ]
    ordering = ['user']

    # Opcional: campos de solo lectura
    readonly_fields = ['latitud', 'longitud']  