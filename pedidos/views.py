from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Cliente, Producto, Pedido, Detalle
from .forms import ClienteForm, DetalleForm

# def menu(request, cliente_id):
#     cliente = get_object_or_404(Cliente, id=cliente_id)
#     if cliente != request.user.cliente and not request.user.is_superuser:
#         return HttpResponse("No tienes acceso a esta cuenta")
    
#     contenido = {
#         'cliente': cliente,
#     }
#     return render(request, 'menu.html', contenido)

def menu(request, cliente_id=None):
    contenido = {}

    if request.user.is_authenticated:
        if cliente_id:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            if cliente != request.user.cliente and not request.user.is_superuser:
                return HttpResponse("No tienes acceso a esta cuenta")
            contenido['cliente'] = cliente
        else:
            # No se envía un cliente_id, pero el usuario está autenticado
            try:
                cliente = request.user.cliente
                contenido['cliente'] = cliente
            except Cliente.DoesNotExist:
                # El usuario no tiene un cliente asociado
                contenido['mensaje'] = "No tienes un cliente asociado"
    else:
        # Usuario no autenticado
        contenido['mensaje'] = "Bienvenido a Detalles Cariño"
    
    return render(request, 'menu.html', contenido)

def main(request):
    
    categoria = request.GET.get('categoria', '')
    
    if categoria:
        productos = Producto.objects.filter(categoria=categoria)
    else:
        productos = Producto.objects.all()
        
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    contenido = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'main.html', contenido)

@login_required #Se puede validar que dependiendo el tipo de usuario se vea una cosa u otra
def pedidos(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente != request.user.cliente and not request.user.is_superuser:
        return HttpResponse("No tienes acceso a esta cuenta")
    
    pedidos = Pedido.objects.filter(cliente=cliente)
    contenido = {
        'cliente': cliente,
        'pedidos': pedidos
    }
    return render(request, 'pedidos.html', contenido)

#@login_required #Se puede validar que dependiendo el tipo de usuario se vea una cosa u otra
def info_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    # if cliente != request.user.cliente and not request.user.is_superuser:
    #     return HttpResponse("No tienes acceso a esta cuenta")
    
    pedidos = Pedido.objects.filter(cliente=cliente)
    contenido = {
        'cliente': cliente,
        'pedidos': pedidos
    }
    return render(request, 'info_cliente.html', contenido)

def main(request):
    # TODO: hay que ajsutar el menu para que no cargue los datos del usuario siempre
    user = request.user     
    categoria = request.GET.get('categoria', '')
    
    if categoria:
        productos = Producto.objects.filter(categoria=categoria)
    else:
        productos = Producto.objects.all()
        
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    contenido = {
        'productos': productos,
        'categorias': categorias,
        'user': user
    }
    return render(request, 'main.html', contenido)

def info_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='extra')
    
    contenido = {
        'producto': producto,
        'personalizaciones': personalizaciones
    }
    return render(request, 'info_productos.html', contenido)

def nuevo_cliente(request):
    mensaje_error = ""
    # Procesa el formulario para un nuevo cliente
    if request.method == "POST":
        # Crear el formulario con los datos del POST
        formulario = ClienteForm(request.POST)
        # Validar el formulario
        if formulario.is_valid():
            # Crear un nuevo cliente con los datos del formulario
            cliente = Cliente.objects.create(
                nombre=formulario.cleaned_data['nombre'],
                cedula=formulario.cleaned_data['cedula'],
                email=formulario.cleaned_data['email'],
                telefono=formulario.cleaned_data['telefono'],
                ciudad=formulario.cleaned_data['ciudad'],
                direccion=formulario.cleaned_data['direccion']
            )
            cliente.save()
            # TODO: redirigir a una pagina del cliente nuevo.
            return HttpResponseRedirect(reverse("menu", args=[cliente.id]))
        else:
            # TODO: Mostrar un mensaje de error, mantenerse en el formulario.
            mensaje_error = "Error en el formulario"
    else:
        # Crear un formulario vacio
        formulario = ClienteForm()
    # Renderizar el formulario
    return render(request, 'nuevo_cliente.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

def nueva_personalizacion(request):
    mensaje_error = ""
    if request.method == "POST":
        formulario = DetalleForm(request.POST, request.FILES)
        if formulario.is_valid():
            personalizacion = Detalle.objects.create(
            # agregar datos de la tabla DETALLE
            )
            personalizacion.save()  
            return HttpResponseRedirect(reverse("nombre_de_la_vista_donde_redirigir"))
        else:
            mensaje_error = "Error en el formulario. Por favor, revisa los datos ingresados."
    else:
        formulario = DetalleForm()
    
    return render(request, 'nueva_personalizacion.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

# def anadir_producto_pedido(request):
#     producto_id = request.GET.get('producto_id', '')
#     cantidad = request.GET.get('cantidad', '')
#     pedido_id = request.COOKIES.get('pedido_id', None)
#     #response = HttpResponse("Cookie Set!")
#     contenido = {}
#     response = render(request, 'borrador.html', contenido)
    
#     if pedido_id:
#         pedido = Pedido.objects.filter(estado_pedido = 'carrito', id = pedido_id).last()
#     else:
#         pedido = None

#     if pedido == None: 
#         pedido = Pedido(estado_pedido = 'borrador')
#         pedido.save()
#         response.set_cookie('pedido_id', pedido.id)

#     producto = Producto.objects.get(id = producto_id)
#     detalle_pedido = PedidoDetalle(pedido=pedido, producto=producto, cantidad= int(cantidad))
#     detalle_pedido.save()
#     return response

# def enviar_correo(request):
#     send_mail("asunto", "mensaje", "correo@gmail.com", ["destinatario", fail_silently=False])