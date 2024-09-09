from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404

from .models import Cliente, Producto, Pedido, Detalle, Item, Destinatario, Pago, Personalizacion
from .forms import ClienteForm, DetalleForm, ProductoForm, ItemForm, DestinatarioPedidoForm, DestinatarioForm, PagoForm, PedidoForm, EmailForm, PagoPedidoForm, EstadoPedidoForm

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

    # Excluir pedidos con estado "cancelado"
    pedidos = pedidos.exclude(estado='Cancelado')
    
    print(pedidos)

    contenido = {
        'cliente': cliente,
        'pedidos': pedidos
    }
    return render(request, 'clientes/pedidos.html', contenido)

@login_required #Se puede validar que dependiendo el tipo de usuario se vea una cosa u otra
def clientes(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if cliente != request.user.cliente and not request.user.is_superuser:
         return HttpResponse("Sin acceso")
    
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

@login_required
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
            producto = formulario.save()
            producto_id = producto.id
            return redirect('productos_items', producto_id)
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = ProductoForm()
    
    # Combina los diccionarios
    contenido_final = {
        'formulario': formulario,
        'mensaje_error': mensaje_error,
        'cliente': request.cliente
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
def productos_items(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='principal')
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
    return render(request, 'items/productos-items.html', contenido)

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
            item.producto = producto  # Asocia el producto con el item
            item.save()
            return HttpResponseRedirect(reverse('productos_items', args=[producto_id]))
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

def detalle_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    formulario = ItemForm(instance=item)
    contenido = {
        'formulario': formulario,
        'item': item,
        'cliente': request.cliente
    }

    return render(request, 'items/editar.html', contenido)

def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
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

def editar_item(request, item_id):
    mensaje_error = ""

    item = get_object_or_404(Item, id=item_id)

    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))

    if "next=" in next_url:
        next_url = next_url.split("next=")[-1]

    print("Next URL:", next_url)
    
    if request.method == "POST":
        formulario = ItemForm(request.POST, request.FILES, instance=item)
        if formulario.is_valid():
            item = formulario.save(commit=False)
            item.imagen = 'productos/Screenshot_2.png'  
            item.save()
            return redirect(next_url)
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        
        formulario = ItemForm(instance=item)
    
    contenido = {
        'formulario': formulario,
        'item': item,
        'mensaje_error': mensaje_error
    }

    return render(request, 'items/editar.html', contenido)

def eliminar_item(request, item_id, producto_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        item.delete()  # Elimina el producto
        return HttpResponseRedirect(reverse('productos_items', args=[producto_id]))

    # Si no es una solicitud POST, puedes redirigir o mostrar un error
    return HttpResponse("Método no permitido", status=405)

# DESTINATARIO
@login_required
def destinatarios(request):
    destinatarios = Destinatario.objects.filter(user_id = request.user.id)
    contenido = {
        'destinatarios': destinatarios,
        'cliente': request.cliente  # Llama al cliente del middleware
    }
    return render(request, 'destinatarios/listado.html', contenido)

def nuevo_destinatario(request, pedido_id=None):
    mensaje_error = ""
    
    if request.method == "POST":
        formulario = DestinatarioForm(request.POST)
        if formulario.is_valid():
            destinatario = formulario.save(commit=False)  # No guardamos todavía
            destinatario.user = request.user  # Asignamos el usuario actual
            destinatario.save()  # Ahora guardamos el destinatario
            
            # Redirigir a la URL deseada
            if pedido_id:
                return redirect('pedido_destinatario_nuevo', pedido_id)
            else:     
                return redirect('destinatarios')
        else:
            mensaje_error = formulario.errors.as_text()
    else:
        formulario = DestinatarioForm()

    # Preparar el contenido para renderizar la plantilla
    contenido = {
        'cliente': request.cliente,  # Llama al cliente del middleware
        'formulario': formulario,
        'mensaje_error': mensaje_error,
    }
    
    return render(request, 'destinatarios/registrar.html', contenido)

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

def nuevo_pago(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        form_pago = PagoForm(request.POST, request.FILES)
        if form_pago.is_valid():
            pago = form_pago.save()

            # Asociar el pago con el pedido
            pedido.pago = pago
            pedido.save()

            return redirect('pedidos2', request.cliente.id)
    else:
        form_pago = PagoForm()

    # Contexto para renderizar el formulario de nuevo en caso de errores
    contenido_final = {
        'formulario': PagoPedidoForm(instance=pedido),
        'formulario_pago': form_pago,
        'cliente': request.cliente,
        'pedido_id': pedido_id
    }

    return render(request, 'pedidos/pago.html', contenido_final)

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

def actualizar_estado_pago(request, pago_id):
    print(pago_id)
    pago = get_object_or_404(Pago, id=pago_id)
    print(pago)

    # Solo cambia el estado si es 'validando'
    if pago.estado == 'Validando':
        pago.estado = 'Pagado'
        pago.save()

    contenido = {
        'cliente': request.user.id
    }

    return redirect(reverse('pedidos'))


# Pedido
@staff_member_required
def pedidos(request):
    estado_pedido = request.GET.get('estado_pedido', '')
    estado_pago = request.GET.get('estado_pago', '')
    
    print(f"Estado del Pedido: {estado_pedido}")
    print(f"Estado del Pago: {estado_pago}")

    pedidos = Pedido.objects.all()

    # Excluir pedidos con estado "Carrito"
    pedidos = pedidos.exclude(estado='Carrito')

    if estado_pedido:
        pedidos = pedidos.filter(estado=estado_pedido)
    if estado_pago:
        pedidos = pedidos.filter(pago__estado=estado_pago)

    productos = Producto.objects.all()
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()

    contenido = {
        'pedidos': pedidos,
        'productos': productos,
        'categorias': categorias,
        'cliente': request.cliente
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

def pedido_crear(request):
    cliente_id = request.session.get('user_id')
    print(f"Cliente ID desde la sesión: {cliente_id}")

    if not cliente_id:
        return HttpResponseRedirect('/')  
    
    # Crea el pedido con estado "Carrito" y el cliente autenticado
    pedido = Pedido.objects.create(
        estado="Carrito",
        cliente_id=request.cliente.id
    )

    # Redirige a la lista de productos con el ID del pedido recién creado
    return redirect('productos_lista', pedido.id)

def productos_lista(request, pedido_id):
    categoria = request.GET.get('categoria', '')
    
    if categoria:
        productos = Producto.objects.filter(categoria=categoria)
    else:
        productos = Producto.objects.all()
        
    categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
    contenido = {
        'productos': productos,
        'categorias': categorias,
        'cliente': request.cliente,  #llamo al cliente del middleware
        'id_pedido': pedido_id
    }
    
    return render(request, 'pedidos/listado-productos.html', contenido)

# @staff_member_required
def lista_productos(request, pedido_id):
    # Obtener el objeto Detalle usando el pedido_id
    producto = get_object_or_404(Detalle, pedido_id=pedido_id)

    print(f'asdasdasdads {producto}')

    # Obtener el ID de la tabla Detalle
    id_detalle = producto.id

    print(f'id_detalle {id_detalle}')

    # Obtener la lista de personalizaciones relacionadas con el producto
    personalizaciones = Personalizacion.objects.filter(detalle_id=id_detalle)

    print(f'personalizaciones {personalizaciones}')

    print(f'request.cliente {request.cliente}')
    
    contenido = {
        'producto': producto,
        'personalizaciones': personalizaciones,
        'cliente': request.cliente
    }
    return render(request, 'pedidos/productos-lista.html', contenido)

def agregar_pedido(request, pedido_id, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    personalizaciones = producto.items.filter(tipo='principal')
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

def agregar_pedido_items(request, pedido_id, producto_id):
    if request.method == 'POST':

        # Imprimir valores para depuración
        print(f"Pedido IDsasdas: {pedido_id}")
        print(f"Producto IDassasasda: {producto_id}")

        producto = get_object_or_404(Producto, id=producto_id)

        # Crear un nuevo detalle
        nuevo_detalle = Detalle.objects.create(
            nombre=producto.nombre,
            imagen=producto.imagen,
            categoria=producto.categoria,
            precio=producto.precio_base,
            pedido_id=pedido_id  # Asignar el pedido_id al nuevo detalle
        )
        
       # Obtener los items seleccionados en el formulario
        selected_items = request.POST.getlist('items')
        print("Items seleccionados:", selected_items)

        selected_cantidades = request.POST.getlist('cantidades')
        print("cantidades seleccionados:", selected_cantidades)

        for item_id in selected_items:
            try:
                # Obtener los valores desde el formulario
                nombre = request.POST.get(f'nombre_{item_id}')
                
                # Reemplazar la coma por un punto antes de la conversión
                precio = float(request.POST.get(f'precio_{item_id}', '0').replace(',', '.'))
                
                tipo = request.POST.get(f'tipo_{item_id}')
                cantidad = int(request.POST.get(f'cantidad_{item_id}', 1))
                total = precio * cantidad  # Calcular el total

                # Depuración: imprimir los valores obtenidos
                print(f"Item ID: {item_id}, Nombre: {nombre}, Precio: {precio}, Tipo: {tipo}, Cantidad: {cantidad}, Total: {total}")

                # Crear la personalización asociada al detalle
                Personalizacion.objects.create(
                    nombre=nombre,
                    precio_individual=precio,
                    cantidad=cantidad,
                    total=total,
                    tipo=tipo,
                    detalle=nuevo_detalle  # Asociar con el detalle recién creado
                )

                contenido = {
                    'cliente': request.cliente  #llamo al cliente del middleware
                }

            except ValueError as e:
                print(f"Error en el procesamiento del item {item_id}: {e}")  # Depuración
                continue

        return redirect(reverse('pedido_destinatario_nuevo', args=[pedido_id]))
    else:
        return HttpResponse('Método no permitido', status=405)

def pedido_destinatario_guardar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = DestinatarioPedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('pedido_pago_cargar', pedido_id)
    else:
        form = DestinatarioPedidoForm(instance=pedido)

    # Combina el contexto del formulario con el cliente y el pedido_id
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente,  # Incluye el cliente del middleware
        'pedido_id': pedido_id       # Asegúrate de pasar el pedido_id al contexto
    }
    
    return redirect('pedidos2', request.cliente.id)

def pedido_destinatario_editar_guardar(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    print ("Holaaaa")
    if request.method == 'POST':
        form = DestinatarioPedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('pedidos2', request.cliente.id)
    else:
        form = DestinatarioPedidoForm(instance=pedido)
    print ("Holaaaa 2")
    # Combina el contexto del formulario con el cliente y el pedido_id
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente,  # Incluye el cliente del middleware
        'pedido_id': pedido_id       # Asegúrate de pasar el pedido_id al contexto
    }
    print ("Holaaaa 3")
    return render(request, 'pedidos/destinatario-actualizar.html', contenido_final)

def pedido_destinatario_nuevo(request, pedido_id):
    destinatarios = Destinatario.objects.filter(user_id=request.user.id)
    print(destinatarios)  # Agrega esta línea para verificar el queryset

    formulario = DestinatarioPedidoForm()
    formulario.fields['destinatario'].queryset = destinatarios
    formulario_destinatario = DestinatarioForm()

    contenido_final = {
        'formulario': formulario,
        'formulario_destinatario': formulario_destinatario,
        'cliente': request.cliente,
        'pedido_id': pedido_id,
    }

    return render(request, 'pedidos/destinatario.html', contenido_final)

def pedido_pago_cargar(request, pedido_id):
    personalizacion = Detalle.objects.filter(pedido_id=pedido_id)
    formulario = PagoPedidoForm()
    formulario_pago = PagoForm()

    contenido_final = {
        'formulario': formulario,
        'formulario_pago': formulario_pago,
        'pedido_id': pedido_id,
        'cliente': request.cliente,
        'personalizacion': personalizacion
    }
    return render(request, 'pedidos/pago.html', contenido_final)

def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    # Solo cambia el estado si es 'Carrito'
    if pedido.estado == 'Carrito':
        pedido.estado = 'Cancelado'
        pedido.save()

    # Obtener el id del cliente asociado al pedido
    cliente_id = pedido.cliente.id if pedido.cliente else None
    
    # Redirige a la vista 'pedidos2' con el id del cliente
    if cliente_id:
        return redirect(reverse('pedidos2', kwargs={'cliente_id': cliente_id}))
    else:
        # Manejar el caso en que el pedido no tiene cliente asociado
        return redirect('pedidos2')  

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    formulario = EstadoPedidoForm(instance=pedido)  # Cargar el formulario con los datos del pedido
    contenido = {
        'formulario': formulario, 
        'pedido': pedido,
        'cliente': request.cliente,  # Llama al cliente del middleware
    }

    return render(request, 'pedidos/editar.html', contenido)

def editar_pedido_estado(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = EstadoPedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()

            estado_seleccionado = form.cleaned_data['estado']
            print(f"Estado seleccionado: {estado_seleccionado}")

            if estado_seleccionado == "En verificacion":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Estamos en proceso de verificar el pago de tu pedido. Tan pronto como la verificación esté completa, "
                    "empezaremos a prepararlo para su envío o recogida.\n\n"
                    "Gracias por tu paciencia."
                )
            elif estado_seleccionado == "Desarrollando":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Tu pago ha sido validado con éxito y estamos trabajando en tu pedido. "
                    "Pronto estará listo para ser recogido en nuestra tienda o enviado a la dirección especificada en el pedido.\n\n"
                    "Agradecemos tu confianza en nosotros."
                )
            elif estado_seleccionado == "Listo":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Nos complace informarte que tu pedido ya está listo para ser retirado y/o enviado.\n\n"
                    "Gracias por tu compra."
                )
            elif estado_seleccionado == "Enviado":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Nos complace informarte que tu pedido ha sido enviado a la dirección especificada.\n\n"
                    "Gracias por tu compra."
                )                
            elif estado_seleccionado == "Entregado":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Tu pedido ha sido entregado con éxito. Esperamos que estés satisfecho con tu compra. "
                    "Si tienes alguna pregunta o necesitas asistencia adicional, no dudes en contactarnos.\n\n"
                    "Gracias por confiar en nosotros."
                )
            elif estado_seleccionado == "Cancelado":
                mensaje_estado = (
                    "Estimado cliente,\n\n"
                    "Lamentamos informarte que tu pedido ha sido cancelado. "
                    "Si necesitas asistencia para realizar un nuevo pedido o tienes alguna pregunta, por favor contáctanos.\n\n"
                    "Gracias por tu comprensión."
                )

            else:
                mensaje_estado = "El estado de tu pedido ha sido actualizado."

            destinatarios_qs = Cliente.objects.filter(user_id=request.user.id).values_list('email', flat=True)

            # Convirtiendo la QuerySet a una lista
            destinatarios = list(destinatarios_qs)

            print(destinatarios)

            destinatario = destinatarios
            asunto = "ACTUALIZACION ESTADO PEDIDO"
            mensaje = mensaje_estado

            # Configurar el envío del correo
            send_mail(
                asunto,  # Asunto del correo
                mensaje,  # Mensaje
                settings.EMAIL_HOST_USER,  # Remitente
                destinatarios,  # Destinatario proporcionado por el usuario
                fail_silently=False,
            )

            return redirect('pedidos') 
    else:
        form = EstadoPedidoForm(instance=pedido)

    # Combina el contexto del formulario con el cliente
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'pedidos/editar.html', contenido_final)

def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            return redirect('pedidos') 
    else:
        form = PedidoForm(instance=pedido)

    # Combina el contexto del formulario con el cliente
    contenido_final = {
        'formulario': form,
        'cliente': request.cliente  # Incluye el cliente del middleware
    }
    
    return render(request, 'pedidos/editar.html', contenido_final)


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

#CORREO

def enviar_correo(request):
    if request.method == "POST":
        formulario = EmailForm(request.POST)
        if formulario.is_valid():
            # Obtener los datos del formulario
            destinatario = formulario.cleaned_data['destinatario']
            asunto = formulario.cleaned_data['asunto']
            mensaje = formulario.cleaned_data['mensaje']

            # Configurar el envío del correo
            send_mail(
                asunto,  # Asunto del correo
                mensaje,  # Mensaje
                settings.EMAIL_HOST_USER,  # Remitente
                [destinatario],  # Destinatario proporcionado por el usuario
                fail_silently=False,
            )

            # Redireccionar después de enviar el correo
            return redirect('correo_enviado')
    else:
        formulario = EmailForm()

    # Renderizar el formulario
    return render(request, 'enviar_correo.html', {'formulario':formulario})

def pedido_actualizar_destinatario(request):
    cliente_id = request.session.get('user_id')
    print(f"Cliente ID desde la sesión: {cliente_id}")

    if not cliente_id:
        return HttpResponseRedirect('/')  
    
    # Crea el pedido con estado "Carrito" y el cliente autenticado
    pedido = Pedido.objects.create(
        estado="Carrito",
        cliente_id=request.cliente.id
    )

    # Redirige a la lista de productos con el ID del pedido recién creado
    return redirect('productos_lista', pedido.id)
#def anadir_producto_pedido(request):
#     producto_id = request.GET.get('producto_id', '')
#     cantidad = request.GET.get('cantidad', '')
#     pedido_id = request.COOKIES.get('pedido_id', None)
#     #response = HttpResponse("Cookie Set!")
#     contenido = {}
#     response = render(request, 'borrador.html', contenido)
    
#     if pedido_id:
#         pedido = Pedido.objects.filter(estado_pedido = 'Carrito', id = pedido_id).last()
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