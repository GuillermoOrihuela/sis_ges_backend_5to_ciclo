from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.inventario.models import Existencia, MovimientoInventario, Kardex, TipoMovimientoInventario

def consultar_stock_disponible(producto_id, almacen_id):
    try:
        existencia = Existencia.objects.get(producto_id=producto_id, almacen_id=almacen_id)
        return existencia.stock_actual
    except Existencia.DoesNotExist:
        return Decimal('0.00')

@transaction.atomic
def registrar_movimiento_inventario(producto_id, almacen_id, tipo_movimiento, cantidad, registrado_por=None, motivo=None):
    # Asegurar que la cantidad sea tratada como Decimal
    cant_decimal = Decimal(str(cantidad))
    
    if cant_decimal <= 0:
        raise ValidationError("La cantidad del movimiento debe ser mayor a cero.")
    
    # Obtener o bloquear existencia
    existencia, created = Existencia.objects.select_for_update().get_or_create(
        producto_id=producto_id,
        almacen_id=almacen_id,
        defaults={'stock_actual': Decimal('0.00'), 'stock_minimo': Decimal('0.00')}
    )

    stock_anterior = existencia.stock_actual

    # Definir si suma o resta
    suma_tipos = [
        TipoMovimientoInventario.ENTRADA, 
        TipoMovimientoInventario.AJUSTE_POSITIVO, 
        TipoMovimientoInventario.DEVOLUCION
    ]
    resta_tipos = [
        TipoMovimientoInventario.SALIDA, 
        TipoMovimientoInventario.AJUSTE_NEGATIVO, 
        TipoMovimientoInventario.VENTA, 
        TipoMovimientoInventario.CONSUMO_SERVICIO
    ]

    if tipo_movimiento in suma_tipos:
        stock_posterior = stock_anterior + cant_decimal
    elif tipo_movimiento in resta_tipos:
        if stock_anterior < cant_decimal and tipo_movimiento in [TipoMovimientoInventario.VENTA, TipoMovimientoInventario.SALIDA, TipoMovimientoInventario.CONSUMO_SERVICIO]:
            raise ValidationError(f"Stock insuficiente para el producto ID {producto_id}. Stock actual: {stock_anterior}, requerido: {cant_decimal}")
        stock_posterior = stock_anterior - cant_decimal
    else:
        raise ValidationError("Tipo de movimiento de inventario inválido.")

    # Actualizar existencia
    existencia.stock_actual = stock_posterior
    existencia.save()

    # Registrar Movimiento
    movimiento = MovimientoInventario.objects.create(
        producto_id=producto_id,
        almacen_id=almacen_id,
        tipo_movimiento=tipo_movimiento,
        cantidad=cant_decimal,
        stock_anterior=stock_anterior,
        stock_posterior=stock_posterior,
        motivo=motivo,
        registrado_por=registrado_por
    )

    # Registrar Kardex
    Kardex.objects.create(
        movimiento=movimiento,
        producto_id=producto_id,
        almacen_id=almacen_id,
        stock_inicial=stock_anterior,
        cantidad=cant_decimal,
        stock_final=stock_posterior,
        tipo_movimiento=tipo_movimiento
    )

    return movimiento