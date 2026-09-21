from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from ...models import Venta, TipoItemVenta
from ...services.venta_service import crear_venta, confirmar_venta, anular_venta
from ..serializers.venta_serializer import VentaSerializer
from apps.servicios.models.servicio import Servicio
from apps.inventario.models import Producto, Almacen
from common.api.mixins import ApiResponseMixin
from common.api.responses import APIResponse
from common.permissions.base import role_permission


def _resolver_almacen_id(request):
    """
    confirmar_venta/anular_venta necesitan un almacén para descontar o
    devolver stock. Antes se asumía a ciegas almacen_id=1, lo que rompía
    en una base de datos recién migrada sin ningún Almacen creado (la
    migración 0002_almacen_por_defecto.py ya siembra uno, pero esta
    función igual valida en tiempo real en vez de repetir el mismo
    supuesto frágil).

    Prioridad: 1) 'almacen' explícito en el body (necesario si hay más de
    un almacén activo), 2) el primer almacén activo existente. Si no hay
    ninguno, se devuelve None y el caller debe responder 400 en vez de
    dejar que la operación reviente más abajo con un error de FK.
    """
    almacen_id = request.data.get('almacen')
    if almacen_id:
        return almacen_id
    primero = Almacen.objects.filter(activo=True).order_by('id').values_list('id', flat=True).first()
    return primero


class VentaViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    'create' arma la venta a través de VentaService.crear_venta (calcula
    subtotales/total; no confirma stock/comisiones todavía — eso ocurre en
    la acción /confirmar/). No se permite editar ni borrar una venta ya
    creada: se corrige anulándola (/anular/) y creando una nueva, para no
    perder el historial contable.
    """
    queryset = Venta.objects.select_related('cliente', 'empleado').prefetch_related('detalles').all().order_by('-fecha')
    serializer_class = VentaSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data
        items_data = validated.pop('items')

        # VentaService espera instancias de Servicio/Producto, no IDs sueltos.
        items_resueltos = []
        for item in items_data:
            resuelto = dict(item)
            if item['tipo_item'] == TipoItemVenta.SERVICIO:
                try:
                    resuelto['servicio'] = Servicio.objects.get(id=item['servicio'])
                except Servicio.DoesNotExist:
                    return APIResponse.error(
                        message=f"El servicio {item['servicio']} no existe.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
            elif item['tipo_item'] == TipoItemVenta.PRODUCTO:
                try:
                    resuelto['producto'] = Producto.objects.get(id=item['producto'])
                except Producto.DoesNotExist:
                    return APIResponse.error(
                        message=f"El producto {item['producto']} no existe.",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
            items_resueltos.append(resuelto)

        try:
            venta = crear_venta(
                empleado=validated['empleado'],
                items_data=items_resueltos,
                cliente=validated.get('cliente'),
                cita=validated.get('cita'),
                descuento_general=validated.get('descuento', 0.00),
            )
        except ValidationError as e:
            return APIResponse.error(
                message=str(e.message if hasattr(e, 'message') else e.args[0]),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        output = self.get_serializer(venta)
        return APIResponse.success(data=output.data, message="Venta registrada correctamente", status_code=status.HTTP_201_CREATED)

    def confirmar(self, request, pk=None):
        almacen_id = _resolver_almacen_id(request)
        if not almacen_id:
            return APIResponse.error(
                message="No hay ningún almacén activo registrado. Crea al menos uno en /gestion/almacenes/ antes de confirmar ventas con productos.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            venta = confirmar_venta(pk, almacen_id=almacen_id, registrado_por=request.user)
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(venta)
        return APIResponse.success(data=serializer.data, message="Venta confirmada correctamente")

    def anular(self, request, pk=None):
        almacen_id = _resolver_almacen_id(request)
        try:
            venta = anular_venta(pk, almacen_id=almacen_id or 1, registrado_por=request.user)
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(venta)
        return APIResponse.success(data=serializer.data, message="Venta anulada correctamente")

    def get_permissions(self):
        if self.action == 'anular':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()
