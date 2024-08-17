from django.contrib import admin
from django.urls import path, include
from pedidos.views import pedidos, main, info_producto, info_cliente, menu, nuevo_cliente
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

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
    path('productos/<int:producto_id>', info_producto, name='info_producto'),                   #Visualizar

    #Clientes
    path('cliente/nuevo', nuevo_cliente, name='nuevo_cliente'),                                 #Agregar
    path('cliente/info/<int:cliente_id>', info_cliente, name='info_cliente'),                   #Info
    path('cliente/pedidos/<int:cliente_id>', pedidos, name='pedidos'),                          #Pedidos
    
    #Carrito
    #path('anadir_producto_pedido/', anadir_producto_pedido, name='anadir_producto_pedido'),    #Agregar

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
