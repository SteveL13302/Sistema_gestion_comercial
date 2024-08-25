from django.contrib import admin
from django.urls import path, include
from pedidos.views import pedidos2, menu, main, clientes, nuevo_cliente, detalle_cliente, editar_cliente, nuevo_producto, productos, eliminar_producto, detalle_producto, editar_producto, nuevo_destinatario, destinatarios, eliminar_destinatario, detalle_destinatario, editar_destinatario, info_producto, nuevo_item, eliminar_item, nuevo_pago, pagos, eliminar_pago, detalle_pago, editar_pago, pedidos, nuevo_pedido, eliminar_pedido, detalle_pedido, editar_pedido
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Autenticación
    path('accounts/', include('allauth.urls')),
         
    #Menu
    path('menu', menu, name='menu'),

    #Panel Admin Django
    path('admin/', admin.site.urls),

    #Home
    path('', main, name='main'),

    #Productos
    path('productos', productos, name='productos'),                                                     #Visualizar
    path('productos/nuevo', nuevo_producto, name='nuevo_producto'),                                     #Registrar
    path('productos/eliminar/<int:producto_id>', eliminar_producto, name='eliminar_producto'),          #Eliminar
    path('productos/editar/<int:producto_id>', detalle_producto, name='detalle_producto'),              #Cargar Datos
    path('productos/editar/guardar/<int:producto_id>', editar_producto, name='editar_producto'),        #Actualizar

    
    #Items
    path('items/<int:producto_id>', info_producto, name='info_producto'),                               #Visualizar
    path('items/nuevo/<int:producto_id>', nuevo_item, name='nuevo_item'),                               #Registrar
    path('items/eliminar/<int:item_id>/<int:producto_id>', eliminar_item, name='eliminar_item'),        #Eliminar

    #Clientes
    path('cliente/nuevo', nuevo_cliente, name='nuevo_cliente'),                                         #Agregar
    path('cliente/info/<int:cliente_id>', clientes, name='clientes'),                                   #Info
    path('cliente/editar/<int:cliente_id>', detalle_cliente, name='detalle_cliente'),                   #Cargar Datos
    path('cliente/editar/guardar/<int:cliente_id>', editar_cliente, name='editar_cliente'),             #Actualizar
    
    #Destinatarios
    path('destinatarios/nuevo', nuevo_destinatario, name='nuevo_destinatario'),                                     #Registrar
    path('destinatarios', destinatarios, name='destinatarios'),                                                     #Consultar
    path('destinatarios/eliminar/<int:destinatario_id>', eliminar_destinatario, name='eliminar_destinatario'),      #Eliminar
    path('destinatarios/editar/<int:destinatario_id>', detalle_destinatario, name='detalle_destinatario'),          #Cargar Datos
    path('destinatarios/editar/guardar/<int:destinatario_id>', editar_destinatario, name='editar_destinatario'),    #Actualizar


    #Pagos
    path('pagos/nuevo', nuevo_pago, name='nuevo_pago'),                                     #Registrar
    path('pagos', pagos, name='pagos'),                                                     #Consultar
    path('pagos/eliminar/<int:pago_id>', eliminar_pago, name='eliminar_pago'),              #Eliminar
    path('pagos/editar/<int:pago_id>', detalle_pago, name='detalle_pago'),                  #Cargar Datos
    path('pagos/editar/guardar/<int:pago_id>', editar_pago, name='editar_pago'),            #Actualizar


    #Pedido
    path('cliente/pedidos/<int:cliente_id>', pedidos2, name='pedidos2'),                          #Pedidos - Cliente en especifico
    path('pedidos', pedidos, name='pedidos'),                                                    #Visualizar
    path('pedidos/nuevo', nuevo_pedido, name='nuevo_pedido'),                                    #Registrar
    path('pedidos/editar/<int:pedido_id>', detalle_pedido, name='detalle_pedido'),              #Cargar Datos
    path('pedidos/editar/guardar/<int:pedido_id>', editar_pedido, name='editar_pedido'),         #Actualizar

    #Carrito
    #path('anadir_producto_pedido/', anadir_producto_pedido, name='anadir_producto_pedido'),    #Agregar

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
