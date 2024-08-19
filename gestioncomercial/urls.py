from django.contrib import admin
from django.urls import path, include
from pedidos.views import pedidos, main, info_cliente, menu, nuevo_cliente, nuevo_producto, productos, eliminar_producto, detalle_producto, editar_producto, info_producto, nuevo_item, eliminar_item
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #Autenticación
    path('accounts/', include('allauth.urls')),
         
    #Menu
    path('menu/<int:cliente_id>', menu, name='menu'),

    #Panel Admin Django
    path('admin/', admin.site.urls),

    #Home
    path('', main, name='main'),

    #Productos
    path('productos/registrar', nuevo_producto, name='nuevo_producto'),                          #Registrar
    path('productos', productos, name='productos'),                          #Consultar
    path('productos/eliminar/<int:producto_id>', eliminar_producto, name='eliminar_producto'),                          #Consultar
    path('productos/editar/<int:producto_id>', detalle_producto, name='detalle_producto'),                   #Visualizar
    path('productos/editar/guardar/<int:producto_id>', editar_producto, name='editar_producto'),                   #Visualizar

    
    #Items
    path('items/<int:producto_id>', info_producto, name='info_producto'),                   #Visualizar
    path('items/registrar/<int:producto_id>', nuevo_item, name='nuevo_item'),                   #Registrar
    path('items/eliminar/<int:item_id>/<int:producto_id>', eliminar_item, name='eliminar_item'),                   #Eliminar

    #Clientes
    path('cliente/nuevo', nuevo_cliente, name='nuevo_cliente'),                                 #Agregar
    path('cliente/info/<int:cliente_id>', info_cliente, name='info_cliente'),                   #Info
    path('cliente/pedidos/<int:cliente_id>', pedidos, name='pedidos'),                          #Pedidos
    
    #Carrito
    #path('anadir_producto_pedido/', anadir_producto_pedido, name='anadir_producto_pedido'),    #Agregar

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
