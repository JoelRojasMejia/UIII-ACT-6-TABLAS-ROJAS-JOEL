from django.contrib import admin
from .models import Usuario, Producto

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'tipo_usuario', 'fecha_registro', 'activo']
    list_filter = ['tipo_usuario', 'activo', 'fecha_registro']
    search_fields = ['nombre', 'email']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'categoria', 'stock', 'disponible']
    list_filter = ['categoria', 'disponible', 'fecha_agregado']
    search_fields = ['nombre', 'descripcion']