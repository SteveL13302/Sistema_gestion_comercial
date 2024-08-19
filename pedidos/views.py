from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Cliente, Producto, Pedido, Detalle, Item
from .forms import ClienteForm, DetalleForm, ProductoForm, ItemForm

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

def productos(request):
    productos = Producto.objects.all()
    contenido = {
        'productos': productos 
    }
    return render(request, 'productos/listado.html', contenido)

def nuevo_producto(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            producto = formulario.save(commit=False)
            producto.imagen = 'productos/Screenshot_2.png' 
            producto.save()
            return redirect('/')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = ProductoForm()
    
    return render(request, 'productos/registro.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.delete()  # Elimina el producto
        return redirect('productos') 

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    formulario = ProductoForm(instance=producto)  # Cargar el formulario con los datos del producto
    
    return render(request, 'productos/editar.html', {'formulario': formulario, 'producto': producto})

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')  # Redirige a la lista de productos después de guardar
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'productos/editar.html', {'formulario': form})

def info_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='extra')
    items = Item.objects.filter(producto=producto)

    # Simplemente creamos una instancia del formulario, pero no lo procesamos aquí
    form = ItemForm()

    contenido = {
        'producto': producto,
        'personalizaciones': personalizaciones,
        'formulario': form,
        'items': items 
    }
    return render(request, 'items/info_productos.html', contenido)

def items(request, producto_id):
    items = Item.objects.all()
    contenido = {
        'productos': items 
    }
    return render(request, 'productos/listado.html', contenido)

def nuevo_item(request, producto_id):
    mensaje_error = ""

    # Obtén el producto usando el ID proporcionado
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == "POST":
        formulario = ItemForm(request.POST, request.FILES)
        if formulario.is_valid():
            item = formulario.save(commit=False)
            item.imagen = 'productos/Screenshot_2.png'  # Modifica si es necesario
            item.producto = producto  # Asocia el producto con el item
            item.save()
            return HttpResponseRedirect(reverse('info_producto', args=[producto_id]))
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        # Pasa el producto al formulario para asegurarte de que esté presente
        formulario = ItemForm(initial={'producto': producto})
    
    return render(request, 'productos/listado.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

def eliminar_item(request, item_id, producto_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item.delete()  # Elimina el producto
        return HttpResponseRedirect(reverse('info_producto', args=[producto_id]))

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)

# def nuevo_cliente(request):
#     mensaje_error = ""
#     # Procesa el formulario para un nuevo cliente
#     if request.method == "POST":
#         # Crear el formulario con los datos del POST
#         formulario = ClienteForm(request.POST)
#         # Validar el formulario
#         if formulario.is_valid():
#             # Crear un nuevo cliente con los datos del formulario
#             cliente = Cliente.objects.create(
#                 nombre=formulario.cleaned_data['nombre'],
#                 cedula=formulario.cleaned_data['cedula'],
#                 email=formulario.cleaned_data['email'],
#                 telefono=formulario.cleaned_data['telefono'],
#                 ciudad=formulario.cleaned_data['ciudad'],
#                 direccion=formulario.cleaned_data['direccion']
#             )
#             cliente.save()
#             # TODO: redirigir a una pagina del cliente nuevo.
#             return HttpResponseRedirect(reverse("menu", args=[cliente.id]))
#         else:
#             # TODO: Mostrar un mensaje de error, mantenerse en el formulario.
#             mensaje_error = "Error en el formulario"
#     else:
#         # Crear un formulario vacio
#         formulario = ClienteForm()
#     # Renderizar el formulario
#     return render(request, 'nuevo_cliente.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

def nuevo_cliente(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = ClienteForm(request.POST)
        if formulario.is_valid():
            cliente = formulario.save(commit=False)
            cliente.user_id = request.user.id 
            cliente.save()
            return redirect('menu', cliente_id=cliente.id)
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = ClienteForm()
    
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