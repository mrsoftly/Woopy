from django.db import models
from django.contrib.auth.models import User

class ApiWoo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)

class Pedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    api = models.ForeignKey(ApiWoo, on_delete=models.CASCADE)
    num_pedido = models.CharField(max_length=100)
    nombre_cliente = models.CharField(max_length=255)
    direccion = models.TextField()
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    numero_telefonico = models.CharField(max_length=20)
    estado_pedido = models.CharField(max_length=50)
    latitud = models.FloatField()
    longitud = models.FloatField()
    fecha_pedido = models.DateTimeField()
    
    
class PedidoOrdenado(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    latitud = models.FloatField()
    longitud = models.FloatField()

class Chofer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    numero_telefonico = models.CharField(max_length=20)
    correo = models.EmailField()

class RutaAsignada(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chofer = models.ForeignKey(Chofer, on_delete=models.CASCADE)
    fecha = models.DateField()
    pedidos_ordenado = models.ManyToManyField(PedidoOrdenado)

class Sucursal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    direccion = models.TextField()
    comuna = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

class Plan(models.Model):
    nombre = models.CharField(max_length=100)
    caracteristicas = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion = models.IntegerField(help_text="Duración en días")
    max_envios_diarios = models.IntegerField(
        null=True, blank=True,
        help_text="Número máximo de envíos por dias (None = sin límite)"
    )

    def __str__(self):
        return self.nombre

class EstadoPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)
    fecha_contratacion = models.DateField()
    fecha_termino = models.DateField()
    activo = models.BooleanField(default=True)

class Pago(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField()
    estado_pago = models.CharField(max_length=50)
    cod_confirmacion = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    raw_data = models.JSONField(blank=True, null=True)  # Para guardar toda la respuesta del SDK/API

    def __str__(self):
        return f"{self.user.username} - {self.estado_pago} - {self.monto}"

