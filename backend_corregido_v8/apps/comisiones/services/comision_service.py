from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.comisiones.models import Comision, EstadoComision
from apps.ventas.models import TipoItemVenta

def calcular_comision(monto_base, porcentaje=Decimal('10.00')):
    return (monto_base * porcentaje) / Decimal('100.00')

@transaction.atomic
def generar_comisiones_venta(venta):
    empleado = venta.empleado
    if not empleado:
        return []

    comisiones_creadas = []
    # Por defecto aplicaremos un 10% configurable o general sobre cada detalle de servicio vendido por el empleado
    porcentaje_defecto = Decimal('10.00')

    for detalle in venta.detalles.filter(tipo_item=TipoItemVenta.SERVICIO):
        monto_base = detalle.subtotal
        monto_comision = calcular_comision(monto_base, porcentaje_defecto)

        comision = Comision.objects.create(
            empleado=empleado,
            venta=venta,
            detalle_venta=detalle,
            monto_base=monto_base,
            porcentaje=porcentaje_defecto,
            monto_comision=monto_comision,
            estado=EstadoComision.PENDIENTE
        )
        comisiones_creadas.append(comision)

    return comisiones_creadas

@transaction.atomic
def aprobar_comision(comision_id):
    try:
        comision = Comision.objects.select_for_update().get(id=comision_id)
    except Comision.DoesNotExist:
        raise ValidationError("La comisión no existe.")
    
    comision.estado = EstadoComision.APROBADA
    comision.save()
    return comision

@transaction.atomic
def registrar_pago_comision(comision_id):
    try:
        comision = Comision.objects.select_for_update().get(id=comision_id)
    except Comision.DoesNotExist:
        raise ValidationError("La comisión no existe.")

    comision.estado = EstadoComision.PAGADA
    comision.save()
    return comision

@transaction.atomic
def anular_comision(comision_id):
    try:
        comision = Comision.objects.select_for_update().get(id=comision_id)
    except Comision.DoesNotExist:
        raise ValidationError("La comisión no existe.")

    comision.estado = EstadoComision.ANULADA
    comision.save()
    return comision