from django.contrib import admin
from .models import Cliente, Producto, Item, Destinatario, Pago, Pedido, Detalle, Personalizacion

class ItemInline(admin.TabularInline):
    model = Item
    extra = 0  # N de formularios vacíos adicionales

class PersonalizacionInline(admin.TabularInline):
    model = Personalizacion
    readonly_fields = ('total',) 
    extra = 0 

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

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'descripcion',
        'imagen',
        'categoria',
        'precio_base',
    )

    inlines = [ItemInline]  #Argega form de items
    readonly_fields = ('precio_base',)  # Campo para solo lectura

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'imagen', 'precio', 'tipo', 'producto')
    list_filter = ('producto',)

@admin.register(Destinatario)
class DestinatarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'ciudad', 'direccion')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id', 'metodo', 'estado', 'comprobante')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'fecha', 'cliente', 'pago', 'destinatario')
    list_filter = ('fecha', 'cliente', 'pago', 'destinatario',)

@admin.register(Detalle)
class DetalleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'imagen', 'categoria', 'precio')
    inlines = [PersonalizacionInline]
    readonly_fields = ('precio',) 

@admin.register(Personalizacion)
class PersonalizacionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'imagen',
        'precio_individual',
        'cantidad',
        'total',
        'tipo',
        'detalle',
    )
    list_filter = ('detalle',)
    readonly_fields = ('total',) 