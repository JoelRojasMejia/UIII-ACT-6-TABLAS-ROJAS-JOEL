from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    
    # URLs para Usuarios
    path('usuarios/agregar/', views.agregar_usuario, name='agregar_usuario'),
    path('usuarios/', views.ver_usuarios, name='ver_usuarios'),
    path('usuarios/actualizar/<int:usuario_id>/', views.actualizar_usuario, name='actualizar_usuario'),
    path('usuarios/borrar/<int:usuario_id>/', views.borrar_usuario, name='borrar_usuario'),
    
    # URLs para Productos
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/', views.ver_productos, name='ver_productos'),
    path('productos/actualizar/<int:producto_id>/', views.actualizar_producto, name='actualizar_producto'),
    path('productos/borrar/<int:producto_id>/', views.borrar_producto, name='borrar_producto'),
    
    # URLs para Catálogo
    path('catalogo/', views.catalogo_productos, name='catalogo_productos'),
    path('catalogo/producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    
    # URLs para Pedidos
    path('pedidos/crear-directo/<int:producto_id>/', views.crear_pedido_directo, name='crear_pedido_directo'),
    path('pedidos/crear-multiple/', views.crear_pedido_multiple, name='crear_pedido_multiple'),
    path('pedidos/', views.ver_pedidos, name='ver_pedidos'),
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/actualizar-estado/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),

    # URLs para MetodoPago (NUEVOS)
    path('pagos/agregar/', views.agregar_metodo_pago, name='agregar_metodo_pago'),
    path('pagos/', views.ver_metodos_pago, name='ver_metodos_pago'),
    path('pagos/actualizar/<int:metodo_pago_id>/', views.actualizar_metodo_pago, name='actualizar_metodo_pago'),
    path('pagos/borrar/<int:metodo_pago_id>/', views.borrar_metodo_pago, name='borrar_metodo_pago'),
    
    # URLs para CuponDescuento (NUEVOS)
    path('cupones/agregar/', views.agregar_cupon_descuento, name='agregar_cupon_descuento'),
    path('cupones/', views.ver_cupones, name='ver_cupones'),
    path('cupones/actualizar/<int:cupon_id>/', views.actualizar_cupon_descuento, name='actualizar_cupon_descuento'),
    path('cupones/borrar/<int:cupon_id>/', views.borrar_cupon_descuento, name='borrar_cupon_descuento'),
    
    # URLs para Resena (NUEVOS)
    path('resenas/', views.ver_resenas, name='ver_resenas'),
    path('resenas/agregar/<int:producto_id>/', views.agregar_resena, name='agregar_resena'),
    path('resenas/borrar/<int:resena_id>/', views.borrar_resena, name='borrar_resena'),
]

# Para servir archivos multimedia en desarrollo (no hay cambios aquí)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
