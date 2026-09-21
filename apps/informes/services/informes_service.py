from django.db.models import Sum, Count, Q, F
from apps.ventas.models import Venta, EstadoVenta
from apps.citas.models import Cita
from apps.inventario.models import Existencia

def generar_informe_ventas(fecha_inicio, fecha_fin):
    ventas = Venta.objects.filter(
        fecha__date__gte=fecha_inicio,
        fecha__date__lte=fecha_fin,
        estado=EstadoVenta.CONFIRMADA
    )
    resumen = ventas.aggregate(
        total_recaudado=Sum('total'),
        total_descuentos=Sum('descuento'),
        cantidad_ventas=Count('id')
    )
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "resumen": resumen,
        "ventas": list(ventas.values('id', 'fecha', 'total', 'cliente__nombres', 'empleado__nombres'))
    }

def generar_informe_citas(fecha_inicio, fecha_fin):
    citas = Cita.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin
    )
    resumen = citas.aggregate(
        total_citas=Count('id'),
        completadas=Count('id', filter=Q(estado='FINALIZADA')),
        canceladas=Count('id', filter=Q(estado='CANCELADA')),
        no_asistio=Count('id', filter=Q(estado='NO_ASISTIO'))
    )
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "resumen": resumen
    }

def generar_informe_inventario_bajo():
    existencias_bajas = Existencia.objects.filter(stock_actual__lte=F('stock_minimo'))
    items = []
    for ex in existencias_bajas:
        items.append({
            "producto": ex.producto.nombre,
            "codigo": ex.producto.codigo,
            "almacen": ex.almacen.nombre,
            "stock_actual": ex.stock_actual,
            "stock_minimo": ex.stock_minimo
        })
    return {
        "items_stock_bajo": items,
        "total_alertas": len(items)
    }