# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required
# from .models import Cliente, Producto, Pedido, PedidoDetalle

# #@login_required
# def ver_pedidos(request, cliente_id):
#     cliente = get_object_or_404(Cliente, id=cliente_id)
#     # if cliente != request.user.cliente and not request.user.is_superuser:
#     #     return HttpResponse("No tienes acceso a esta cuenta")
#     pedidos = cliente.clientes.all()
#     contenido = {
#         'cliente': cliente,
#         'pedidos': pedidos
#     }
#     return render(request, 'pedidos.html', contenido)

# def ver_productos(request):
#     categoria = request.GET.get('categoria', '')
    
#     if categoria:
#         productos = Producto.objects.filter(categoria=categoria)
#     else:
#         productos = Producto.objects.all()
        
#     categorias = Producto.objects.values_list('categoria', flat=True).distinct()
    
#     contenido = {
#         'productos': productos,
#         'categorias': categorias
#     }
#     return render(request, 'productos.html', contenido)

# def ver_info_producto(request, producto_id):
#     producto = get_object_or_404(Producto, id=producto_id)
#     personalizaciones = producto.items.filter(tipo='extra')
    
#     contenido = {
#         'producto': producto,
#         'personalizaciones': personalizaciones
#     }
#     return render(request, 'info_productos.html', contenido)

# def ver_borrador(request):
#     return render(request, 'borrador.html')


# # def anadir_producto_pedido(request):
# #     producto_id = request.GET.get('producto_id', '')
# #     cantidad = request.GET.get('cantidad', '')
# #     pedido_id = request.COOKIES.get('pedido_id', None)
# #     #response = HttpResponse("Cookie Set!")
# #     contenido = {}
# #     response = render(request, 'borrador.html', contenido)
    
# #     if pedido_id:
# #         pedido = Pedido.objects.filter(estado_pedido = 'carrito', id = pedido_id).last()
# #     else:
# #         pedido = None

# #     if pedido == None: 
# #         pedido = Pedido(estado_pedido = 'borrador')
# #         pedido.save()
# #         response.set_cookie('pedido_id', pedido.id)

# #     producto = Producto.objects.get(id = producto_id)
# #     detalle_pedido = PedidoDetalle(pedido=pedido, producto=producto, cantidad= int(cantidad))
# #     detalle_pedido.save()
# #     return response

# # def enviar_correo(request):
# #     send_mail("asunto", "mensaje", "correo@gmail.com", ["destinatario", fail_silently=False])