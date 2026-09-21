from django.db import transaction
from django.core.exceptions import ValidationError
from apps.ventas.models import Venta, DetalleVenta, EstadoVenta, TipoItemVenta
from apps.inventario.services.inventario_service import registrar_movimiento_inventario
from apps.inventario.models import TipoMovimientoInventario, ConsumoServicio

@transaction.atomic
def crear_venta(empleado, items_data, cliente=None, cita=None, descuento_general=0.00):
    from decimal import Decimal

    venta = Venta.objects.create(
        cliente=cliente,
        empleado=empleado,
        cita=cita,
        descuento=descuento_general,
        estado=EstadoVenta.BORRADOR
    )

    subtotal_acumulado = Decimal('0.00')

    for item in items_data:
        tipo = item.get('tipo_item')
        cantidad = Decimal(str(item.get('cantidad', 1.00)))
        descuento_item = Decimal(str(item.get('descuento', '0.00')))
        
        if tipo == TipoItemVenta.SERVICIO:
            servicio = item.get('servicio')
            precio = Decimal(str(item.get('precio_unitario') or servicio.precio))
            descripcion = servicio.nombre
            sub = (precio * cantidad) - descuento_item
            
            DetalleVenta.objects.create(
                venta=venta,
                tipo_item=TipoItemVenta.SERVICIO,
                servicio=servicio,
                descripcion=descripcion,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=descuento_item,
                subtotal=sub
            )
            subtotal_acumulado += sub

        elif tipo == TipoItemVenta.PRODUCTO:
            producto = item.get('producto')
            precio = Decimal(str(item.get('precio_unitario') or producto.precio_venta))
            descripcion = producto.nombre
            sub = (precio * cantidad) - descuento_item

            DetalleVenta.objects.create(
                venta=venta,
                tipo_item=TipoItemVenta.PRODUCTO,
                producto=producto,
                descripcion=descripcion,
                cantidad=cantidad,
                precio_unitario=precio,
                descuento=descuento_item,
                subtotal=sub
            )
            subtotal_acumulado += sub

    venta.subtotal = subtotal_acumulado
    venta.total = max(Decimal('0.00'), subtotal_acumulado - Decimal(str(venta.descuento)))
    venta.save()
    return venta

@transaction.atomic
def confirmar_venta(venta_id, almacen_id=1, registrado_por=None):
    try:
        venta = Venta.objects.select_for_update().get(id=venta_id)
    except Venta.DoesNotExist:
        raise ValidationError("La venta no existe.")

    if venta.estado == EstadoVenta.CONFIRMADA:
        raise ValidationError("La venta ya se encuentra confirmada.")
    if venta.estado == EstadoVenta.ANULADA:
        raise ValidationError("No se puede confirmar una venta anulada.")

    # Procesar inventario para cada detalle
    for detalle in venta.detalles.all():
        if detalle.tipo_item == TipoItemVenta.PRODUCTO and detalle.producto:
            # Descontar stock por venta
            registrar_movimiento_inventario(
                producto_id=detalle.producto.id,
                almacen_id=almacen_id,
                tipo_movimiento=TipoMovimientoInventario.VENTA,
                cantidad=detalle.cantidad,
                registrado_por=registrado_por,
                motivo=f"Venta confirmada #{venta.id}"
            )
        elif detalle.tipo_item == TipoItemVenta.SERVICIO and detalle.servicio:
            # Descontar insumos asociados al servicio si existen
            consumos = ConsumoServicio.objects.filter(servicio=detalle.servicio)
            for consumo in consumos:
                cantidad_total_consumo = consumo.cantidad_estimada * detalle.cantidad
                registrar_movimiento_inventario(
                    producto_id=consumo.producto.id,
                    almacen_id=almacen_id,
                    tipo_movimiento=TipoMovimientoInventario.CONSUMO_SERVICIO,
                    cantidad=cantidad_total_consumo,
                    registrado_por=registrado_por,
                    motivo=f"Consumo por servicio {detalle.servicio.name if hasattr(detalle.servicio, 'name') else detalle.servicio.nombre} (Venta #{venta.id})"
                )

    venta.estado = EstadoVenta.CONFIRMADA
    venta.save()

    # Generar comisiones automáticamente
    from apps.comisiones.services.comision_service import generar_comisiones_venta
    generar_comisiones_venta(venta)

    return venta

@transaction.atomic
def anular_venta(venta_id, almacen_id=1, registrado_por=None):
    try:
        venta = Venta.objects.select_for_update().get(id=venta_id)
    except Venta.DoesNotExist:
        raise ValidationError("La venta no existe.")

    if venta.estado == EstadoVenta.ANULADA:
        raise ValidationError("La venta ya está anulada.")

    # Si estaba confirmada, devolver stock al inventario
    if venta.estado == EstadoVenta.CONFIRMADA:
        for detalle in venta.detalles.all():
            if detalle.tipo_item == TipoItemVenta.PRODUCTO and detalle.producto:
                registrar_movimiento_inventario(
                    producto_id=detalle.producto.id,
                    almacen_id=almacen_id,
                    tipo_movimiento=TipoMovimientoInventario.DEVOLUCION,
                    cantidad=detalle.cantidad,
                    registrado_por=registrado_por,
                    motivo=f"Anulación de venta #{venta.id}"
                )

    venta.estado = EstadoVenta.ANULADA
    venta.save()
    return venta