from django.db import models
import os

# --- Modelos Existentes ---

class Usuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('vendedor', 'Vendedor'),
        ('administrador', 'Administrador'),
    ]
    
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='cliente')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"

class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('ropa', 'Ropa'),
        ('accesorios', 'Accesorios'),
        ('zapatos', 'Zapatos'),
        ('belleza', 'Belleza'),
        ('hogar', 'Hogar'),
    ]
    
    TALLA_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('Única', 'Única'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    talla = models.CharField(max_length=10, choices=TALLA_CHOICES, blank=True, null=True)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    disponible = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    def actualizar_stock(self, cantidad_vendida):
        """Actualiza el stock del producto después de un pedido confirmado."""
        self.stock -= cantidad_vendida
        self.save()

class MetodoPago(models.Model):
    """Nueva tabla: Métodos de Pago."""
    TIPO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
        ('efectivo', 'Pago en Efectivo/Entrega'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class CuponDescuento(models.Model):
    """Nueva tabla: Cupones de Descuento."""
    codigo = models.CharField(max_length=50, unique=True)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)  # Ejemplo: 10.00 para 10%
    fecha_expiracion = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.codigo} ({self.descuento_porcentaje}%)"

class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    estado_pedido = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    direccion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)  # Fecha en que se confirma el pedido
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    productos = models.ManyToManyField(Producto, through='ItemPedido')
    # Nuevos campos de relación
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    cupon = models.ForeignKey(CuponDescuento, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    def __str__(self):
        return f"Pedido {self.id_pedido} - {self.id_usuario.nombre}"
    
    def total_pedido(self):
        # Lógica para calcular el total, incluyendo descuento si hay un cupón.
        total = sum(item.subtotal() for item in self.items.all())
        if self.cupon and self.cupon.activo:
            total -= total * (self.cupon.descuento_porcentaje / 100)
        return total

    def confirmar_pedido(self):
        """Confirmar el pedido y actualizar el stock de productos."""
        self.estado_pedido = 'confirmado'
        self.fecha_confirmacion = models.DateTimeField(auto_now_add=True)
        for item in self.items.all():
            item.producto.actualizar_stock(item.cantidad)
        self.save()

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    
    def subtotal(self):
        return self.producto.precio * self.cantidad
    
    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"
        
class Resena(models.Model):
    """Nueva tabla: Reseñas/Calificaciones de Producto."""
    CALIFICACION_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='resenas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resenas')
    calificacion = models.PositiveSmallIntegerField(choices=CALIFICACION_CHOICES)
    comentario = models.TextField(blank=True, null=True)
    fecha_resena = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Asegura que un usuario solo pueda dejar una reseña por producto
        unique_together = ('producto', 'usuario')

    def __str__(self):
        return f"Reseña de {self.usuario.nombre} para {self.producto.nombre} ({self.calificacion} estrellas)"
