from django.contrib import admin
from .models import Cliente, Producto, Destinatario, Item, Pago, Pedido, Detalle, Personalizacion

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0  # Número de formularios vacíos adicionales que se mostrarán

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'descripcion',
        'imagen',
        'precio_base',
        'categoria',
    )
    inlines = [ItemInline]
    readonly_fields = ('precio_base',)  # Hace que el campo precio_base sea de solo lectura

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'imagen', 'precio', 'tipo', 'producto')
    list_filter = ('producto',)

# El resto de los modelos
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'contrasenia',
        'cedula',
        'email',
        'telefono',
        'ciudad',
        'direccion',
    )

@admin.register(Destinatario)
class DestinatarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'ciudad', 'direccion')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'metodo', 'estado', 'comprobante')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha', 'estado', 'pago')
    list_filter = ('cliente', 'fecha', 'pago')
