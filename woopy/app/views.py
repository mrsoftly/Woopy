from woocommerce import API
import googlemaps
from app.comunas import states as comunas
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ApiWoo, Pedido, PedidoOrdenado, Chofer, RutaAsignada, Sucursal, Plan
from django import forms
import math
import folium
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from django.contrib.auth.models import User
import os
from dotenv import load_dotenv
@login_required
def logout_view(request):
    return redirect('home')
class apiform(forms.ModelForm):
    class Meta:
        model = ApiWoo
        fields = ['url', 'consumer_key', 'consumer_secret']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar la apariencia del formulario
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Ingresa {field.label.lower()}'
            })
  # Asegúrate de que esté bien importado

def guardar_api_validacion(request):
    # 🔍 Verificamos si ya existe la configuración
    try:
        apiwoo = ApiWoo.objects.get(user=request.user)
        return redirect('dashboard')
    except ApiWoo.DoesNotExist:
        pass  # No existe, continuar con la creación

    if request.method == 'POST':
        form = apiform(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']

            if not url.startswith('http'):
                messages.error(request, 'La URL debe comenzar con http:// o https://')
                return render(request, 'cargarapi.html', {'form': form})

            # Guardar nueva configuración
            api_instance = form.save(commit=False)
            api_instance.user = request.user
            api_instance.save()

            messages.success(request, 'API configurada exitosamente.')
            return redirect('dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return render(request, 'cargarapi.html', {'form': form})

    # Método GET: mostrar formulario vacío
    

@login_required
def dashboard(request):
    try:
        apiwoo = ApiWoo.objects.get(user=request.user)
        
    except ApiWoo.DoesNotExist:
        apiwoo = None
        pedido = None
    pedido = Pedido.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'pedido': pedido, 'apiwoo': apiwoo})
@login_required
def cargar_pedidos(request):
    # Obtener credenciales del usuario para WooCommerce
    apiwoo = ApiWoo.objects.get(user=request.user)
    url = apiwoo.url
    cons_key = apiwoo.consumer_key
    secret = apiwoo.consumer_secret
    api_id = apiwoo.id
    user_id = request.user.id

    # Inicializar API de WooCommerce
    wcapi = API(
        url=url,
        consumer_key=cons_key,
        consumer_secret=secret,
        wp_api=True,
        version="wc/v3",
    )

    # Obtener pedidos completados desde WooCommerce
    pedidos = wcapi.get("orders", params={"status": "completed", "per_page": 20}).json()
    print(f"Pedidos obtenidos: {len(pedidos)}")
    # Inicializar cliente de Google Maps
    gmaps = googlemaps.Client(key='AIzaSyBXFGcOYMk4wE8PbyPR_El8K7sr2c-LCrQ')

    nuevos_pedidos_guardados = 0
    orden = []

    for pedido in pedidos:
        id_woo = pedido['id']
        print(f"Procesando pedido ID: {id_woo}")

        # Obtener comuna y convertir código si es necesario
        comuna = pedido['shipping']['state']
        for key, value in comunas.items():
            if comuna == key:
                comuna = value

        # Verificar si el pedido ya existe en la base de datos
        existe = Pedido.objects.filter(num_pedido=id_woo, user_id=user_id).exists()
        print(f"¿Pedido {id_woo} ya existe? {existe}")

        if not existe:
            # Construir dirección completa
            direccion_completa = f"{pedido['shipping']['address_1']}, {comuna}, {pedido['shipping']['city']}"
            print(f"Geocodificando: {direccion_completa}")

            # Geocodificar dirección
            result = gmaps.geocode(direccion_completa)
            if result:
                latitud = result[0]['geometry']['location']['lat']
                longitud = result[0]['geometry']['location']['lng']

                # Agregar a la lista orden (opcional, para uso posterior)
                orden.append({
                    'user_id': user_id,
                    'api_id': api_id,
                    'num_pedido': id_woo,
                    'nombre_cliente': f"{pedido['billing']['first_name']} {pedido['billing']['last_name']}",
                    'direccion': pedido['shipping']['address_1'],
                    'comuna': comuna,
                    'region': pedido['shipping']['city'],
                    'numero_telefonico': pedido['billing']['phone'],
                    'estado_pedido': pedido['status'],
                    'latitud': latitud,
                    'longitud': longitud,
                    'fecha_pedido': pedido['date_created']
                })

                # Guardar el pedido en la base de datos
                ped = Pedido(
                    user=request.user,
                    api_id=api_id,
                    num_pedido=id_woo,
                    nombre_cliente=f"{pedido['billing']['first_name']} {pedido['billing']['last_name']}",
                    direccion=pedido['shipping']['address_1'],
                    comuna=comuna,
                    region=pedido['shipping']['city'],
                    numero_telefonico=pedido['billing']['phone'],
                    estado_pedido=pedido['status'],
                    latitud=latitud,
                    longitud=longitud,
                    fecha_pedido=pedido['date_created']
                )
                ped.save()
                nuevos_pedidos_guardados += 1

                print(f"Pedido {id_woo} guardado exitosamente")
            else:
                print(f"No se pudo geocodificar la dirección: {direccion_completa}")
        else:
            print(f"Pedido {id_woo} ya existe, saltando...")

    print(f"Total de pedidos nuevos guardados: {nuevos_pedidos_guardados}")
    return redirect('dashboard')  # Redirigir al dashboard después de cargar los pedidos



@login_required
def org_pedidos(request):
    # Coordenadas iniciales (punto de inicio)
    lat_ini, long_ini = -33.5137037, -70.6580167
    inicio = (lat_ini, long_ini)

    # Obtener pedidos del usuario
    pedidos = Pedido.objects.filter(user=request.user).order_by('fecha_pedido')
    pedidos_org = PedidoOrdenado.objects.filter(user=request.user)
    # Verificar si ya existen pedidos ordenados para el usuario
   
    if pedidos_org.exists():
        
        return render(request,'pedidos.html',{'org': pedidos_org})

    if request.method == 'POST':
        # Construir lista de puntos incluyendo el inicio
        orden = [{'id': 0, 'coord': inicio}]
        for item in pedidos:
            orden.append({
                'id': item.id,
                'user_id': item.user.id,
                'coord': (item.latitud, item.longitud),
                'nombre':item.nombre_cliente,
            })

        # Función de distancia euclidiana (en metros aprox.)
        def euclidean_distance(coord1, coord2):
            return int(math.hypot(coord1[0] - coord2[0], coord1[1] - coord2[1]) * 100000)

        # Matriz de distancias
        dist_matrix = [
            [euclidean_distance(a['coord'], b['coord']) for b in orden]
            for a in orden
        ]

        # Configurar modelo de ruteo
        manager = pywrapcp.RoutingIndexManager(len(dist_matrix), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return dist_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Parámetros de búsqueda
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

        # Resolver problema
        solution = routing.SolveWithParameters(search_params)

        if solution:
            route = []
            index = routing.Start(0)
            while not routing.IsEnd(index):

                node_index = manager.IndexToNode(index)
                route.append(node_index)
                if node_index != 0:
                    nuevos =PedidoOrdenado(
                        user=User.objects.get(id=orden[node_index]['user_id']),
                        pedido_id=orden[node_index]['id'],
                        latitud=orden[node_index]['coord'][0],
                        longitud=orden[node_index]['coord'][1]
                    )
                    nuevos.save()
                index = solution.Value(routing.NextVar(index))

            route.append(manager.IndexToNode(index))  # Agregar nodo final

            # Crear mapa con folium
            m = folium.Map(location=inicio, zoom_start=12)

            for idx, node_index in enumerate(route):
                lat, lon = orden[node_index]['coord']
                if node_index == 0:
                    html = f"""
                        <h4>Datos del cliente</h4>
                        <p>Punto {idx}: ID {orden[node_index]['id']}</p>
                    """
                    folium.Marker(
                        location=(lat, lon),
                        popup=html,
                        icon=folium.Icon(color="green" if idx == 0 else "blue")
                    ).add_to(m)
                else:
                    html = f"""
                        <h4>Datos del cliente</h4>
                        <p>Punto {idx}: ID {orden[node_index]['id']}</p>
                        Cliente: {orden[node_index]['nombre']}<br>
                    """
                    folium.Marker(
                        location=(lat, lon),
                        popup=html,
                        icon=folium.Icon(color="green" if idx == 0 else "blue")
                    ).add_to(m)


            # Dibujar la línea de la ruta
            ruta_coords = [orden[i]['coord'] for i in route]
            folium.PolyLine(locations=ruta_coords, color="green", weight=3).add_to(m)
            save = 'app/templates/rutas'
            # Guardar el archivo HTML
            
            mapa =f"{request.user}maps.html"
            file = os.path.join(save,mapa)
            m.save(file)
            

            
        else:
            print("No se pudo encontrar una solución para la ruta.")

    return render(request, 'pedidos.html', {'pedido': pedidos})

   
@login_required
def ver_mapa(request):
    id = request.user
    return render (request,f"rutas/{id}maps.html")
    

    
    
