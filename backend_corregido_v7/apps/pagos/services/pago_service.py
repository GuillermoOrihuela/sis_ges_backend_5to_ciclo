from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from apps.pagos.models import Pago, EstadoPago
from apps.ventas.models import Venta, EstadoVenta

@transaction.atomic
def registrar_pago(venta_id, monto, metodo_pago, referencia=None, registrado_por=None):
    try:
        venta = Venta.objects.select_for_update().get(id=venta_id)
    except Venta.DoesNotExist:
        raise ValidationError("La venta no existe.")

    if venta.estado == EstadoVenta.ANULADA:
        raise ValidationError("No se pueden registrar pagos en ventas anuladas.")

    # Calcular total pagado previamente
    pagos_existentes = Pago.objects.filter(venta=venta, estado=EstadoPago.PAGADO).aggregate(total_pagado=Sum('monto'))['total_pagado'] or 0
    from decimal import Decimal
    pagos_existentes = Decimal(str(pagos_existentes))
    monto_dec = Decimal(str(monto))

    saldo_pendiente = venta.total - pagos_existentes
    if monto_dec > saldo_pendiente:
        raise ValidationError(f"El monto excede el saldo pendiente de la venta. Saldo actual: {saldo_pendiente}")

    pago = Pago.objects.create(
        venta=venta,
        monto=monto_dec,
        metodo_pago=metodo_pago,
        estado=EstadoPago.PAGADO,
        referencia=referencia,
        registrado_por=registrado_por
    )

    return pago

@transaction.atomic
def anular_pago(pago_id):
    try:
        pago = Pago.objects.select_for_update().get(id=pago_id)
    except Pago.DoesNotExist:
        raise ValidationError("El pago no existe.")

    pago.estado = EstadoPago.ANULADO
    pago.save()
    return pago