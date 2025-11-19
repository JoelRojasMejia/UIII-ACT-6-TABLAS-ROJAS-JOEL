from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import models # Añade esta línea
from django.db.models import Avg # Importar Avg para calcular el promedio de reseñas

# Importar todos los modelos, incluyendo los nuevos
from .models import Usuario, Producto, Pedido, ItemPedido, MetodoPago, CuponDescuento, Resena

def index(request):
    """Página de inicio/base."""
    return render(request, 'base.html')

# =================================================================================
# ========== VISTAS PARA USUARIOS ==========

def agregar_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        tipo_usuario = request.POST.get('tipo_usuario')
        # 'activo' debe ser True si existe en POST, False si no (por el checkbox)
        activo = request.POST.get('activo') == 'on' 
        
        Usuario.objects.create(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            tipo_usuario=tipo_usuario,
            activo=activo
        )
        return redirect('ver_usuarios')
    
    return render(request, 'usuario/agregar_usuario.html')

def ver_usuarios(request):
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    return render(request, 'usuario/ver_usuarios.html', {'usuarios': usuarios})

def actualizar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre')
        usuario.email = request.POST.get('email')
        usuario.telefono = request.POST.get('telefono')
        usuario.direccion = request.POST.get('direccion')
        usuario.tipo_usuario = request.POST.get('tipo_usuario')
        usuario.activo = request.POST.get('activo') == 'on'
        usuario.save()
        return redirect('ver_usuarios')
    
    return render(request, 'usuario/actualizar_usuario.html', {'usuario': usuario})

def borrar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    
    if request.method == 'POST':
        usuario.delete()
        return redirect('ver_usuarios')
    
    return render(request, 'usuario/borrar_usuario.html', {'usuario': usuario})

# =================================================================================
# ========== VISTAS PARA PRODUCTOS ==========

def agregar_producto(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio = float(request.POST.get('precio'))
            categoria = request.POST.get('categoria')
            talla = request.POST.get('talla')
            color = request.POST.get('color')
            stock = int(request.POST.get('stock'))
            disponible = request.POST.get('disponible') == 'on'
            
            # Obtener el archivo de imagen de request.FILES
            imagen_subida = request.FILES.get('imagen') 
            
            producto = Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                categoria=categoria,
                talla=talla,
                color=color,
                stock=stock,
                disponible=disponible,
                # Asignar la imagen si fue subida
                imagen=imagen_subida if imagen_subida else None 
            )
            
            return redirect('ver_productos')
        except Exception as e:
            return render(request, 'producto/agregar_producto.html', {'error': str(e)})
    
    return render(request, 'producto/agregar_producto.html')

def ver_productos(request):
    productos = Producto.objects.all().order_by('-fecha_agregado')
    return render(request, 'producto/ver_productos.html', {'productos': productos})

def actualizar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        try:
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion')
            producto.precio = float(request.POST.get('precio'))
            producto.categoria = request.POST.get('categoria')
            producto.talla = request.POST.get('talla')
            producto.color = request.POST.get('color')
            producto.stock = int(request.POST.get('stock'))
            producto.disponible = request.POST.get('disponible') == 'on'
            
            # Manejar la actualización de la imagen
            if 'imagen' in request.FILES:
                # Esto reemplazará la imagen existente (y la anterior podría borrarse si se usa un almacenamiento adecuado)
                producto.imagen = request.FILES['imagen']
            
            producto.save()
            return redirect('ver_productos')
        except Exception as e:
            return render(request, 'producto/actualizar_producto.html', {'producto': producto, 'error': str(e)})
    
    return render(request, 'producto/actualizar_producto.html', {'producto': producto})

def borrar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.delete()
        return redirect('ver_productos')
    
    return render(request, 'producto/borrar_producto.html', {'producto': producto})

# =================================================================================
# ========== VISTAS PARA CATÁLOGO Y PEDIDOS ==========

def catalogo_productos(request):
    productos = Producto.objects.filter(disponible=True, stock__gt=0).order_by('-fecha_agregado')
    categorias = Producto.CATEGORIA_CHOICES
    categoria_seleccionada = request.GET.get('categoria', '')
    
    if categoria_seleccionada:
        productos = productos.filter(categoria=categoria_seleccionada)
    
    # Calcular calificación promedio para cada producto y pasar el conteo de reseñas
    productos_con_calificacion = []
    for producto in productos:
        # Usa .annotate() para obtener el promedio y el conteo de una vez (más eficiente si lo usaras en el QuerySet)
        # Pero mantendremos tu lógica de agregación aquí para no reescribir demasiado.
        resena_data = producto.resenas.aggregate(Avg('calificacion'), count=models.Count('id'))
        promedio = resena_data['calificacion__avg']
        
        producto.calificacion_promedio = round(promedio, 1) if promedio else None
        productos_con_calificacion.append(producto)

    return render(request, 'catalogo/catalogo.html', {
        'productos': productos_con_calificacion,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada
    })

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    resenas = producto.resenas.all().order_by('-fecha_resena')
    
    resena_data = producto.resenas.aggregate(Avg('calificacion'), count=models.Count('id'))
    promedio = resena_data['calificacion__avg']
    total_resenas = resena_data['count'] # Nueva variable para el conteo

    calificacion_promedio = round(promedio, 1) if promedio else None
    
    context = {
        'producto': producto,
        'resenas': resenas,
        'media_calificacion': calificacion_promedio, # Renombrado para coincidir con template sugerido
        'total_resenas': total_resenas, # Nueva variable para el conteo de reseñas
    }
    return render(request, 'catalogo/detalle_producto.html', context)

def crear_pedido_directo(request, producto_id):
    if request.method == 'POST':
        try:
            usuario_id = request.POST.get('usuario_id')
            direccion = request.POST.get('direccion')
            cantidad = int(request.POST.get('cantidad', 1))
            metodo_pago_id = request.POST.get('metodo_pago') 
            cupon_codigo = request.POST.get('cupon_codigo') 
            
            usuario = get_object_or_404(Usuario, id=usuario_id)
            producto = get_object_or_404(Producto, id=producto_id)
            metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id) if metodo_pago_id else None
            cupon = get_object_or_404(CuponDescuento, codigo=cupon_codigo, activo=True) if cupon_codigo else None

            if cantidad > producto.stock:
                return render(request, 'pedidos/crear_pedido_directo.html', {
                    'producto': producto,
                    'usuarios': Usuario.objects.filter(activo=True, tipo_usuario='cliente'),
                    'metodos_pago': MetodoPago.objects.filter(activo=True),
                    'error': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.'
                })
            
            pedido = Pedido.objects.create(
                id_usuario=usuario,
                direccion=direccion,
                metodo_pago=metodo_pago, 
                cupon=cupon, 
            )
            
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad
            )
            
            producto.stock -= cantidad
            producto.save()
            
            return redirect('ver_pedidos')
            
        except Exception as e:
            producto = get_object_or_404(Producto, id=producto_id)
            usuarios = Usuario.objects.filter(activo=True, tipo_usuario='cliente')
            metodos_pago = MetodoPago.objects.filter(activo=True)
            return render(request, 'pedidos/crear_pedido_directo.html', {
                'producto': producto,
                'usuarios': usuarios,
                'metodos_pago': metodos_pago,
                'error': str(e)
            })
    
    producto = get_object_or_404(Producto, id=producto_id)
    usuarios = Usuario.objects.filter(activo=True, tipo_usuario='cliente')
    metodos_pago = MetodoPago.objects.filter(activo=True) 
    return render(request, 'pedidos/crear_pedido_directo.html', {
        'producto': producto,
        'usuarios': usuarios,
        'metodos_pago': metodos_pago 
    })

def crear_pedido_multiple(request):
    if request.method == 'POST':
        try:
            usuario_id = request.POST.get('usuario_id')
            direccion = request.POST.get('direccion')
            productos_seleccionados = request.POST.getlist('productos')
            metodo_pago_id = request.POST.get('metodo_pago') 
            cupon_codigo = request.POST.get('cupon_codigo') 
            
            usuario = get_object_or_404(Usuario, id=usuario_id)
            metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id) if metodo_pago_id else None
            cupon = get_object_or_404(CuponDescuento, codigo=cupon_codigo, activo=True) if cupon_codigo else None

            
            pedido = Pedido.objects.create(
                id_usuario=usuario,
                direccion=direccion,
                metodo_pago=metodo_pago, 
                cupon=cupon, 
            )
            
            for producto_id in productos_seleccionados:
                producto = get_object_or_404(Producto, id=producto_id)
                cantidad = int(request.POST.get(f'cantidad_{producto_id}', 1))
                
                if cantidad > producto.stock:
                    pedido.delete()
                    return render(request, 'pedidos/crear_pedido_multiple.html', {
                        'usuarios': Usuario.objects.filter(activo=True, tipo_usuario='cliente'),
                        'productos': Producto.objects.filter(disponible=True, stock__gt=0),
                        'metodos_pago': MetodoPago.objects.filter(activo=True),
                        'error': f'Stock insuficiente para {producto.nombre}. Solo hay {producto.stock} unidades.'
                    })
                
                ItemPedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad
                )
                
                producto.stock -= cantidad
                producto.save()
            
            return redirect('ver_pedidos')
            
        except Exception as e:
            return render(request, 'pedidos/crear_pedido_multiple.html', {
                'usuarios': Usuario.objects.filter(activo=True, tipo_usuario='cliente'),
                'productos': Producto.objects.filter(disponible=True, stock__gt=0),
                'metodos_pago': MetodoPago.objects.filter(activo=True),
                'error': str(e)
            })
    
    usuarios = Usuario.objects.filter(activo=True, tipo_usuario='cliente')
    productos = Producto.objects.filter(disponible=True, stock__gt=0)
    metodos_pago = MetodoPago.objects.filter(activo=True) 
    return render(request, 'pedidos/crear_pedido_multiple.html', {
        'usuarios': usuarios,
        'productos': productos,
        'metodos_pago': metodos_pago 
    })

def ver_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    return render(request, 'pedidos/ver_pedidos.html', {'pedidos': pedidos})

def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})

def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_pedido')
        pedido.estado_pedido = nuevo_estado
        pedido.save()
        return redirect('ver_pedidos')
    
    return render(request, 'pedidos/actualizar_estado.html', {'pedido': pedido})

# =================================================================================
# ========== VISTAS PARA MetodoPago ==========

def agregar_metodo_pago(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        activo = request.POST.get('activo') == 'on'
        
        MetodoPago.objects.create(
            nombre=nombre,
            tipo=tipo,
            activo=activo
        )
        return redirect('ver_metodos_pago')
        
    tipos_pago = MetodoPago.TIPO_CHOICES
    return render(request, 'metodo_pago/agregar_metodo_pago.html', {'tipos_pago': tipos_pago})

def ver_metodos_pago(request):
    metodos = MetodoPago.objects.all().order_by('nombre')
    return render(request, 'metodo_pago/ver_metodos_pago.html', {'metodos': metodos})

def actualizar_metodo_pago(request, metodo_pago_id):
    metodo = get_object_or_404(MetodoPago, id=metodo_pago_id)
    
    if request.method == 'POST':
        metodo.nombre = request.POST.get('nombre')
        metodo.tipo = request.POST.get('tipo')
        metodo.activo = request.POST.get('activo') == 'on'
        metodo.save()
        return redirect('ver_metodos_pago')
        
    tipos_pago = MetodoPago.TIPO_CHOICES
    return render(request, 'metodo_pago/actualizar_metodo_pago.html', {'metodo': metodo, 'tipos_pago': tipos_pago})

def borrar_metodo_pago(request, metodo_pago_id):
    metodo = get_object_or_404(MetodoPago, id=metodo_pago_id)
    
    if request.method == 'POST':
        metodo.delete()
        return redirect('ver_metodos_pago')
        
    return render(request, 'metodo_pago/borrar_metodo_pago.html', {'metodo': metodo})

# =================================================================================
# ========== VISTAS PARA CuponDescuento ==========

def agregar_cupon_descuento(request):
    if request.method == 'POST':
        try:
            codigo = request.POST.get('codigo')
            descuento_porcentaje = float(request.POST.get('descuento_porcentaje'))
            fecha_expiracion = request.POST.get('fecha_expiracion')
            activo = request.POST.get('activo') == 'on'
            
            CuponDescuento.objects.create(
                codigo=codigo,
                descuento_porcentaje=descuento_porcentaje,
                fecha_expiracion=fecha_expiracion if fecha_expiracion else None,
                activo=activo
            )
            return redirect('ver_cupones')
        except Exception as e:
            return render(request, 'cupon/agregar_cupon.html', {'error': str(e)})

    return render(request, 'cupon/agregar_cupon.html')

def ver_cupones(request):
    cupones = CuponDescuento.objects.all().order_by('-fecha_expiracion')
    return render(request, 'cupon/ver_cupones.html', {'cupones': cupones})

def actualizar_cupon_descuento(request, cupon_id):
    cupon = get_object_or_404(CuponDescuento, id=cupon_id)
    
    if request.method == 'POST':
        try:
            cupon.codigo = request.POST.get('codigo')
            cupon.descuento_porcentaje = float(request.POST.get('descuento_porcentaje'))
            fecha_expiracion = request.POST.get('fecha_expiracion')
            cupon.fecha_expiracion = fecha_expiracion if fecha_expiracion else None
            cupon.activo = request.POST.get('activo') == 'on'
            cupon.save()
            return redirect('ver_cupones')
        except Exception as e:
            return render(request, 'cupon/actualizar_cupon.html', {'cupon': cupon, 'error': str(e)})

    return render(request, 'cupon/actualizar_cupon.html', {'cupon': cupon})

def borrar_cupon_descuento(request, cupon_id):
    cupon = get_object_or_404(CuponDescuento, id=cupon_id)
    
    if request.method == 'POST':
        cupon.delete()
        return redirect('ver_cupones')
        
    return render(request, 'cupon/borrar_cupon.html', {'cupon': cupon})

# =================================================================================
# ========== VISTAS PARA Resena (NUEVAS) ==========

def agregar_resena(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    usuarios = Usuario.objects.filter(activo=True, tipo_usuario='cliente')
    
    if request.method == 'POST':
        try:
            usuario_id = request.POST.get('usuario_id')
            calificacion = int(request.POST.get('calificacion'))
            comentario = request.POST.get('comentario')
            
            usuario = get_object_or_404(Usuario, id=usuario_id)

            # Prevenir que un usuario reseñe el mismo producto dos veces
            if Resena.objects.filter(producto=producto, usuario=usuario).exists():
                return render(request, 'resena/agregar_resena.html', {
                    'producto': producto,
                    'usuarios': usuarios,
                    'calificaciones': Resena.CALIFICACION_CHOICES,
                    'error': 'Ya existe una reseña de este usuario para este producto.'
                })
            
            Resena.objects.create(
                producto=producto,
                usuario=usuario,
                calificacion=calificacion,
                comentario=comentario
            )
            # Redirigir al detalle del producto después de guardar la reseña
            return redirect('detalle_producto', producto_id=producto.id) 
        except Exception as e:
            return render(request, 'resena/agregar_resena.html', {
                'producto': producto,
                'usuarios': usuarios,
                'calificaciones': Resena.CALIFICACION_CHOICES,
                'error': str(e)
            })
            
    # Obtener las opciones de calificación del modelo para el template
    calificaciones = Resena.CALIFICACION_CHOICES 
    return render(request, 'resena/agregar_resena.html', {
        'producto': producto,
        'usuarios': usuarios,
        'calificaciones': calificaciones
    })

def ver_resenas(request):
    resenas = Resena.objects.all().order_by('-fecha_resena')
    return render(request, 'resena/ver_resenas.html', {'resenas': resenas})

def borrar_resena(request, resena_id):
    resena = get_object_or_404(Resena, id=resena_id)
    
    if request.method == 'POST':
        producto_id = resena.producto.id
        resena.delete()
        # Redirigir al detalle del producto después de borrar la reseña
        return redirect('detalle_producto', producto_id=producto_id)
        
    return render(request, 'resena/borrar_resena.html', {'resena': resena})