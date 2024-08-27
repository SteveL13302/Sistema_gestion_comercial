from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Cliente, Producto, Pedido, Detalle, Item, Destinatario, Pago, Personalizacion
from .forms import ClienteForm, DetalleForm, ProductoForm, ItemForm, DestinatarioForm, PagoForm, PedidoForm, EmailForm

# MENU      
# def menu(request): 
#     return render(request, 'menu.html')


# HOME      
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
        'cliente': request.cliente  #llamo al cliente del middleware
    }
    
    return render(request, 'main.html', contenido)


# CLIENTE   
#@login_required #Se puede validar que dependiendo el tipo de usuario se vea una cosa u otra
def pedidos2(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente != request.user.cliente and not request.user.is_superuser:
        return HttpResponse("No tienes acceso a esta cuenta")
    
    pedidos = Pedido.objects.filter(cliente=cliente)
    contenido = {
        'cliente': cliente,
        'pedidos': pedidos
    }
    return render(request, 'clientes/pedidos.html', contenido)

@login_required #Se puede validar que dependiendo el tipo de usuario se vea una cosa u otra
def clientes(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente != request.user.cliente and not request.user.is_superuser:
         return HttpResponse("No tienes acceso a esta cuenta")
    
    pedidos = Pedido.objects.filter(cliente=cliente)
    contenido = {
        'cliente': cliente,
        'pedidos': pedidos
    }
    return render(request, 'clientes/info_cliente.html', contenido)

def nuevo_cliente(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = ClienteForm(request.POST)
        if formulario.is_valid():
            # Si el usuario ya tiene un cliente, evita duplicados
            if Cliente.objects.filter(user=request.user).exists():
                mensaje_error = "Ya tienes un cliente asociado."
                return render(request, 'clientes/registrar.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

            cliente = formulario.save(commit=False)
            cliente.user = request.user
            cliente.save()
            return redirect('main')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = ClienteForm()
    
    return render(request, 'clientes/registrar.html', {'formulario': formulario, 'mensaje_error': mensaje_error})

def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    formulario = ClienteForm(instance=cliente)
    contenido = {
        'formulario': formulario, 
        'cliente': cliente,
        'cliente': request.cliente  # Llama al cliente del middleware
    }

    return render(request, 'clientes/editar.html', contenido)

@login_required
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente != request.user.cliente and not request.user.is_superuser:
         return HttpResponse("No tienes acceso a esta cuenta")
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.user = request.user  # Establecer el campo user con el usuario actual
            cliente.save()
            return redirect('clientes', cliente_id=cliente.id)
    else:
        form = ClienteForm(instance=cliente)

    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'clientes/editar.html', contenido_final)


# PRODUCTO  
@staff_member_required
def productos(request):
    productos = Producto.objects.all()
    contenido = {
        'productos': productos,
        'cliente': request.cliente  #llamo al cliente del middleware
    }
    return render(request, 'productos/listado.html', contenido)

@staff_member_required
def nuevo_producto(request):
    mensaje_error = ""

    if request.method == "POST":
        formulario = ProductoForm(request.POST, request.FILES) 
        if formulario.is_valid():
            formulario.save()
            return redirect('/')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = ProductoForm()

    contenido_final = {
        'formulario': formulario,
        'mensaje_error': mensaje_error,
        'cliente': getattr(request, 'cliente', None)
    }

    return render(request, 'productos/registrar.html', contenido_final)

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.delete()  # Elimina el producto
        return redirect('productos') 

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)


@staff_member_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    formulario = ProductoForm(instance=producto)  # Cargar el formulario con los datos del producto
    contenido = {
        'formulario': formulario, 
        'producto': producto,
        'cliente': request.cliente,  # Llama al cliente del middleware
    }

    return render(request, 'productos/editar.html', contenido)


@staff_member_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos')  # Redirige a la lista de productos después de guardar
    else:
        form = ProductoForm(instance=producto)

    # Combina el contexto del formulario con el cliente
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'productos/editar.html', contenido_final)

@staff_member_required
def info_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='base')
    items = Item.objects.filter(producto=producto)

    # Creamos una instancia del formulario, pero no lo procesamos aquí
    form = ItemForm()

    contenido = {
        'producto': producto,
        'personalizaciones': personalizaciones,
        'formulario': form,
        'items': items ,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    return render(request, 'items/info_productos.html', contenido)

# ITEM   
@staff_member_required
def items(request):
    items = Item.objects.all()
    contenido = {
        'productos': items,
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

    contenido = {
        'formulario': formulario, 
        'mensaje_error': mensaje_error,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'productos/listado.html', contenido)

def eliminar_item(request, item_id, producto_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item.delete()  # Elimina el producto
        return HttpResponseRedirect(reverse('info_producto', args=[producto_id]))

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)


# DESTINATARIO
@staff_member_required
def destinatarios(request):
    destinatarios = Destinatario.objects.all()
    contenido = {
        'destinatarios': destinatarios,
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    return render(request, 'destinatarios/listado.html', contenido)

def nuevo_destinatario(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = DestinatarioForm(request.POST)
        if formulario.is_valid():
            destinatario = formulario.save()
            return redirect('destinatarios')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = DestinatarioForm()

    contenido = {
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    
    contenido_final = {
        'formulario': formulario,
        'mensaje_error': mensaje_error,
        **contenido
    }
    
    return render(request, 'destinatarios/registrar.html', contenido_final)

def eliminar_destinatario(request, destinatario_id):
    destinatario = get_object_or_404(Destinatario, id=destinatario_id)
    
    if request.method == 'POST':
        destinatario.delete()  # Elimina el destinatario
        return redirect('destinatarios')

    return HttpResponse("Método no permitido", status=405)

def detalle_destinatario(request, destinatario_id):
    destinatario = get_object_or_404(Destinatario, id=destinatario_id)
    formulario = DestinatarioForm(instance=destinatario)
    contenido = {
        'formulario': formulario, 
        'destinatario': destinatario,
        'cliente': request.cliente  # Llama al cliente del middleware
    }

    return render(request, 'destinatarios/editar.html', contenido)

def editar_destinatario(request, destinatario_id):
    destinatario = get_object_or_404(Destinatario, id=destinatario_id)
    
    if request.method == 'POST':
        form = DestinatarioForm(request.POST, instance=destinatario)
        if form.is_valid():
            form.save()
            return redirect('destinatarios')
    else:
        form = DestinatarioForm(instance=destinatario)

    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'destinatarios/editar.html', contenido_final)


# PAGO
@staff_member_required
def pagos(request):
    pagos = Pago.objects.all()
    contenido = {
        'pagos': pagos,
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    return render(request, 'pagos/listado.html', contenido)

def nuevo_pago(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = PagoForm(request.POST, request.FILES)
        if formulario.is_valid():
            pago = formulario.save(commit=False)
            pago.comprobante = 'comprobantes/comprobante-default.jpg'
            pago.save()
            return redirect('pagos')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = PagoForm()

    contenido = {
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    
    contenido_final = {
        'formulario': formulario,
        'mensaje_error': mensaje_error,
        **contenido
    }
    
    return render(request, 'pagos/registrar.html', contenido_final)

def eliminar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    
    if request.method == 'POST':
        pago.delete()  # Elimina el pago
        return redirect('pagos')

    return HttpResponse("Método no permitido", status=405)

def detalle_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    formulario = PagoForm(instance=pago)
    contenido = {
        'formulario': formulario, 
        'pago': pago,
        'cliente': request.cliente  # Llama al cliente del middleware
    }

    return render(request, 'pagos/editar.html', contenido)

def editar_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    
    if request.method == 'POST':
        form = PagoForm(request.POST, request.FILES, instance=pago)
        if form.is_valid():
            form.save()
            return redirect('pagos')
    else:
        form = PagoForm(instance=pago)

    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'pagos/editar.html', contenido_final)


# Pedido
@staff_member_required
def pedidos(request):
    pedidos = Pedido.objects.all()
    productos = Producto.objects.all()

    contenido = {
        'pedidos': pedidos,
        'cliente': request.cliente,  # Llama al cliente del middleware
        'productos': productos,
    }
    return render(request, 'pedidos/listado.html', contenido)

def nuevo_pedido(request):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = PedidoForm(request.POST)
        if formulario.is_valid():
            pedido = formulario.save(commit=False)
            pedido.save()
            return redirect('pedidos')  # Redirige a la lista de pedidos después de guardar
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = PedidoForm()

    contenido = {
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    
    # Combina los diccionarios
    contenido_final = {
        'formulario': formulario,
        'mensaje_error': mensaje_error,
        **contenido
    }
    
    return render(request, 'pedidos/registrar.html', contenido_final)

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        pedido.delete()  # Elimina el pedido
        return redirect('pedidos') 

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    formulario = PedidoForm(instance=pedido)  # Cargar el formulario con los datos del pedido
    contenido = {
        'formulario': formulario, 
        'pedido': pedido,
        'cliente': request.cliente,  # Llama al cliente del middleware
    }

    return render(request, 'pedidos/editar.html', contenido)

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('pedidos')  # Redirige a la lista de pedidos después de guardar
    else:
        form = PedidoForm(instance=pedido)

    # Combina el contexto del formulario con el cliente
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'pedidos/editar.html', contenido_final)

def agregar_pedido(request, pedido_id, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='base')
    items = Item.objects.filter(producto=producto)

    # Creamos una instancia del formulario, pero no lo procesamos aquí
    form = ItemForm()

    contenido = {
        'producto': producto,
        'personalizaciones': personalizaciones,
        'formulario': form,
        'items': items ,
        'cliente': request.cliente,  
        'pedido_id': pedido_id  
    }
    return render(request, 'pedidos/seleccion-productos.html', contenido)

def agregar_pedido_items(request):
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        producto_id = request.POST.get('producto_id')

        print(f"request ID: {request}")

        # Imprimir valores para depuración
        print(f"Pedido ID: {pedido_id}")
        print(f"Producto ID: {producto_id}")

        # Crear un nuevo detalle
        nuevo_detalle = Detalle.objects.create(
            nombre=Detalle.nombre,
            imagen=Detalle.imagen,
            categoria=Detalle.categoria,
            precio=Detalle.precio,
            pedido_id=pedido_id  # Asignar el pedido_id al nuevo detalle
        )
        
        # Procesar cada personalización seleccionada
        for key, value in request.POST.items():
            if key.startswith('cantidad_'):
                item_id = key.split('_')[1]
                try:
                    cantidad = int(value)
                    if cantidad > 0:
                        personalizacion = Personalizacion.objects.get(id=item_id)
                        Personalizacion.objects.create(
                            nombre=personalizacion.nombre,
                            precio_individual=personalizacion.precio_individual,
                            cantidad=cantidad,
                            total=personalizacion.precio_individual * cantidad,
                            tipo=personalizacion.tipo,
                            detalle=nuevo_detalle
                        )
                except (Personalizacion.DoesNotExist, ValueError):
                    continue

        return redirect('detalle_pedido', pedido_id=pedido_id)
    else:
        return HttpResponse('Método no permitido', status=405)

# DETALLE      
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

#def anadir_producto_pedido(request):
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

def enviar_correo(request):
    if request.method == "POST":
        formulario = EmailForm(request.POST)
        if formulario.is_valid():
            correo_usuario = formulario.cleaned_data['correo_usuario']
            asunto = formulario.cleaned_data['asunto']
            mensaje = formulario.cleaned_data['mensaje']

            # Configurar el envío del correo
            send_mail(
                asunto,  # Asunto del correo
                f"Mensaje de: {correo_usuario}\n\n{mensaje}",  # Mensaje incluyendo el correo del usuario
                settings.EMAIL_HOST_USER,  # Remitente
                ['stevenesparza36@gmail.com'],  # Destinatario fijo
                fail_silently=False,
            )

            return redirect('correo_enviado')  # Redireccionar después de enviar
    else:
        formulario = EmailForm()

    return render(request, 'enviar_correo.html', {'formulario': formulario})