from django.db import models
#from django.contrib.auth.models import User

class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    contrasenia = models.CharField(max_length=50)
    cedula = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=10)
    direccion = models.TextField(max_length=200)
    #user = models.OneToOneField(User, related_name='cliente', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.nombre}, {self.cedula}"

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(max_length=200)
    imagen = models.ImageField(upload_to='productos/')
    categoria = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)

    def calcular_precio_base(self):
        self.precio_base = sum(item.precio for item in self.items.filter(tipo='base'))  # Usar 'items' como related_name
    
    def save(self, *args, **kwargs):
        if self.pk:  # Si el producto ya tiene un ID
            self.calcular_precio_base()  # Calcula el precio base
        super().save(*args, **kwargs)  # Guarda el producto con el precio base actualizado
    
    def __str__(self) -> str:
        return f"{self.nombre}"

class Item(models.Model):
    opc_producto = [("base", "Producto Base"), ("extra", "Personalización")]

    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='items/', null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50, choices=opc_producto)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="items", default=1)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Guarda el ítem primero
        # Actualiza el precio base del producto al que pertenece este ítem
        self.producto.calcular_precio_base()
        self.producto.save(update_fields=['precio_base'])

    def __str__(self) -> str:
        return f"{self.nombre}, {self.tipo}"

class Destinatario(models.Model):
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=10)
    direccion = models.TextField(max_length=200)

    def __str__(self) -> str:
        return f"{self.nombre}, {self.direccion}"

class Pago(models.Model):
    opc_metodo = [("transferencia", "Transferencia"),("tarjeta", "Tarjeta")]
    opc_estado_pago = [("pagado", "Pagado"),("pendiente", "Pendiente")]

    metodo = models.CharField(max_length=50, choices=opc_metodo)
    estado = models.CharField(max_length=50, choices=opc_estado_pago, default="pendiente")
    comprobante = models.ImageField(upload_to='comprobantes/')

    def __str__(self) -> str:
        return f"{self.metodo}, {self.estado}"

class Pedido(models.Model):
    opc_estado = [("enviado", "Enviado"),("pendiente", "Pendiente"),("entregado", "Entregado"),("carrito", "Carrito")]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="clientes", null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, choices=opc_estado, default="pendiente")
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="pagos", null=True, blank=True)

    def calcular_total(self):
        return sum([detalle.total for detalle in self.detalles.all()])

    def __str__(self) -> str:
        #return f"{self.id}, Total: {self.calcular_total()}"
        return f"{self.id}, Total: {self.cliente}"

class PedidoDetalle(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pedidos")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="detalles")
    destinatario = models.ForeignKey(Destinatario, on_delete=models.CASCADE, related_name="destinatarios", null=True, blank=True)
    cantidad = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calcular_total(self):
        return self.cantidad * self.producto.precio_base

    def save(self, *args, **kwargs):
        # Antes de guardar, calcula y asigna el total
        self.total = self.calcular_total()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.pedido.id}, Producto: {self.producto.nombre}, Total: {self.total}"
