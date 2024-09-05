
from django import forms
from .models import Cliente, Producto, Item, Destinatario, Pago, Pedido, Detalle, Personalizacion

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'cedula', 'email', 'telefono', 'ciudad', 'direccion', 'user']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nombre Apellido'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0123456789'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0987654321'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Santo Domingo'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle Principal, Calle Secundaria, Referencia'}),
            'user': forms.HiddenInput(),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'imagen', 'categoria', 'precio_base']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Producto XYZ'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ej: Descripción del producto'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Categoría'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.00'}),   #Gestionar para que calcule en base al modelo
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        # fields = ['nombre', 'imagen', 'precio', 'tipo', 'producto']
        fields = ['nombre', 'imagen', 'precio', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nombre del ítem'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.00'}),    #Gestionar para que calcule en base al modelo
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            # 'producto': forms.Select(attrs={'class': 'form-control'}),
            # 'producto': forms.HiddenInput(),
        }

class DestinatarioForm(forms.ModelForm):
    class Meta:
        model = Destinatario
        fields = ['nombre', 'telefono', 'ciudad', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nombre del destinatario'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0987654321'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Ciudad'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ej: Dirección completa'}),
        }

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['metodo', 'estado', 'comprobante']
        widgets = {
            'metodo': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'comprobante': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['destinatario']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'pago': forms.Select(attrs={'class': 'form-control'}),
            'destinatario': forms.Select(attrs={'class': 'form-control'}),
        }

class DetalleForm(forms.ModelForm):
    class Meta:
        model = Detalle
        fields = ['nombre', 'imagen', 'categoria', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nombre del detalle'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Categoría'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.00'}),    #Gestionar para que calcule en base al modelo
        }

class PersonalizacionForm(forms.ModelForm):
    class Meta:
        model = Personalizacion
        fields = ['nombre', 'imagen', 'precio_individual', 'cantidad', 'total', 'tipo', 'detalle']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Nombre de la personalización'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'precio_individual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.00'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1'}),
            'total': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 0.00'}),     #Gestionar para que calcule en base al modelo
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'detalle': forms.Select(attrs={'class': 'form-control'}),
        }

class EmailForm(forms.Form):
    destinatario = forms.EmailField(
        label="Destinatario", 
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo del destinatario'})
    )
    asunto = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto del correo'})
    )
    mensaje = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje aquí'})
    )