from django.contrib import admin
from django.urls import path, include
# from pedidos.views import ver_pedidos, ver_productos, ver_borrador, ver_info_producto
from django.conf import settings
from django.conf.urls.static import static
 

urlpatterns = [
    # path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    # path('pedidos/<int:cliente_id>', ver_pedidos, name='ver_pedidos_cliente'),
    # path('productos/', ver_productos, name='ver_productos'),
    # path('info-productos/<int:producto_id>', ver_info_producto, name='ver_info_producto'),
    #path('anadir_producto_pedido/', anadir_producto_pedido, name='anadir_producto_pedido'),

    # path('borrador/', ver_borrador, name='ver_borrador')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
