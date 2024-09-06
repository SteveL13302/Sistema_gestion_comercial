from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    cedula = models.CharField(max_length=10)
    email = models.EmailField()
    telefono = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    user = models.OneToOneField(User, related_name='cliente', on_delete=models.CASCADE, null=True, blank=True, unique=True)

    class Meta:
        db_table = 'cliente' 
    
    def __str__(self) -> str:
        return f"{self.nombre}, {self.cedula}, {self.id}"

class Producto(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(max_length=200)
    imagen = models.ImageField(upload_to='media/productos/', default='productos/producto-default.jpg' , null=True, blank=True)
    categoria = models.CharField(max_length=100)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)

    def calcular_precio_base(self):
        self.precio_base = sum(item.precio for item in self.items.filter(tipo='base'))  
    
    def save(self, *args, **kwargs):
        if self.pk:  # Si el producto ya tiene un ID
            self.calcular_precio_base()  # Calcula el precio base
        super().save(*args, **kwargs)  # Guarda el producto con el precio base actualizado
    
    def __str__(self) -> str:
        return f"{self.nombre}"

class Item(models.Model):
    OPC_PRODUCTO = [("base", "Producto Base"), ("extra", "Personalización")]

    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='items/', null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50, choices=OPC_PRODUCTO)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="items")

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
    ciudad = models.CharField(max_length=30)
    direccion = models.TextField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self) -> str:
        return f"{self.nombre}, {self.direccion}"

class Pago(models.Model):
    OPC_METODO = [("transferencia", "Transferencia"),("tarjeta", "Tarjeta")]
    OPC_ESTADO_PAGO = [("pagado", "Pagado"),("validadando", "Validadando")]

    metodo = models.CharField(max_length=50, choices=OPC_METODO)
    estado = models.CharField(max_length=50, choices=OPC_ESTADO_PAGO, default="validadando")
    comprobante = models.ImageField(upload_to='media/comprobantes/', default='comprobantes/comprobante-default.jpg',  null=True, blank=True)       #Cambiar que se puede enviar vacio

    def __str__(self) -> str:
        return f"{self.estado}"

class Pedido(models.Model):
    OPC_ESTADO_PEDIDO = [("carrito", "Carrito"),("enviado", "Enviado"),("entregado", "Entregado")]
    
    estado = models.CharField(max_length=15, choices=OPC_ESTADO_PEDIDO, default="carrito")
    fecha = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="clientes", null=True, blank=True)
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name="pagos", null=True, blank=True)
    destinatario = models.ForeignKey(Destinatario, on_delete=models.CASCADE, related_name="destinatarios", null=True, blank=True)

    # TODO: Verificar si la funcion calcular total se va a ocupar aqui???????????????????????????????????
    def calcular_total(self):
        return sum([detalle.total for detalle in self.detalles.all()])

    def __str__(self) -> str:
        #return f"{self.id}, Total: {self.calcular_total()}"
        return f"{self.id}, {self.cliente}, {self.destinatario}"

class Detalle(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='productos/', default='productos/producto-default.jpg' , null=True, blank=True) # Quitar para que se suba el archivo // llamar a la imagen directa del producto
    categoria = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="pedidos", blank=True, null=True)
    
    def calcular_precio(self):
        self.precio = sum(personalizacion.total for personalizacion in self.personalizaciones.filter(tipo='base'))  
    
    def save(self, *args, **kwargs):
        if self.pk:  # Si el producto ya tiene un ID
            self.calcular_precio()  # Calcula el precio base
        super().save(*args, **kwargs)  # Guarda el producto con el precio base actualizado
    
    def __str__(self) -> str:
        return f"{self.nombre}"

class Personalizacion(models.Model):
    OPC_DETALLE = [("base", "Producto Base"), ("extra", "Personalización")]

    nombre = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='items/', default='productos/producto-default.jpg' , null=True, blank=True)  # Quitar para que se suba el archivo // llamar a la imagen directa del producto
    precio_individual = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=50, choices=OPC_DETALLE)
    detalle = models.ForeignKey(Detalle, on_delete=models.CASCADE, related_name="personalizaciones")

    def calcular_total(self):
        self.total = self.precio_individual * self.cantidad 
    
    def save(self, *args, **kwargs):
        self.calcular_total()    # calcula total antes de guardar
        super().save(*args, **kwargs)  # Guarda
        
        self.detalle.calcular_precio()  # Vuelve a calcular el precio del detalle
        self.detalle.save(update_fields=['precio']) # Actualiza el precio del detalle al que pertenece este ítem

    def __str__(self) -> str:
        return f"{self.nombre}, {self.tipo}"