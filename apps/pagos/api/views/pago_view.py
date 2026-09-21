from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ...models.pago import Pago, EstadoPago
from ...services import pago_service
from ..serializers.pago_serializer import PagoSerializer, RegistrarPagoSerializer
from common.api.mixins import ApiResponseMixin
from common.api.responses import APIResponse
from common.permissions.base import role_permission


class PagoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    'create' pasa por PagoService.registrar_pago (valida que el monto no
    exceda el saldo pendiente de la venta). No se permite editar un pago:
    para corregirlo hay que anularlo (/anular/) y registrar uno nuevo, igual
    que con Ventas, para no perder el rastro contable.
    """
    queryset = Pago.objects.select_related('venta').all().order_by('-fecha')
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['venta', 'estado', 'metodo_pago']

    def get_queryset(self):
        # Filtro por fecha exacta (no lo puede hacer filterset_fields solo,
        # porque 'fecha' es DateTimeField): usado por la pantalla de Caja
        # para listar los pagos de un día concreto.
        qs = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        if fecha:
            qs = qs.filter(fecha__date=fecha)
        return qs

    def create(self, request, *args, **kwargs):
        input_serializer = RegistrarPagoSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            pago = pago_service.registrar_pago(
                venta_id=data['venta'],
                monto=data['monto'],
                metodo_pago=data['metodo_pago'],
                referencia=data.get('referencia'),
                registrado_por=request.user,
            )
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)

        output = self.get_serializer(pago)
        return APIResponse.success(data=output.data, message="Pago registrado correctamente", status_code=status.HTTP_201_CREATED)

    def anular(self, request, pk=None):
        try:
            pago = pago_service.anular_pago(pk)
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(pago)
        return APIResponse.success(data=serializer.data, message="Pago anulado correctamente")

    def get_permissions(self):
        if self.action == 'anular':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()


class CajaResumenAPIView(APIView):
    """
    GET /api/v1/gestion/caja/resumen/?fecha=YYYY-MM-DD

    No existe un modelo "Caja" dedicado en el Contrato Técnico (ver
    INTEGRACION_BACKEND.md, punto 11 y el propio PendingModule del
    frontend), así que este endpoint arma el resumen de caja del día como
    una agregación de Pago + Venta, en vez de inventar un modelo nuevo sin
    validarlo primero con el equipo. Si más adelante se necesita apertura /
    cierre de caja con montos declarados a mano, eso sí requiere un modelo
    dedicado (CajaSesion o similar) — se deja fuera de este alcance.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha_str = request.query_params.get('fecha')
        if fecha_str:
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                return APIResponse.error(
                    message="El parámetro 'fecha' debe tener el formato YYYY-MM-DD.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        else:
            fecha = timezone.localdate()

        pagos_del_dia = Pago.objects.filter(fecha__date=fecha, estado=EstadoPago.PAGADO)

        por_metodo = list(
            pagos_del_dia.values('metodo_pago')
            .annotate(total=Sum('monto'))
            .order_by('metodo_pago')
        )
        total_ingresos = pagos_del_dia.aggregate(total=Sum('monto'))['total'] or 0

        anulados_del_dia = Pago.objects.filter(fecha__date=fecha, estado=EstadoPago.ANULADO)
        total_anulado = anulados_del_dia.aggregate(total=Sum('monto'))['total'] or 0

        return APIResponse.success(
            data={
                "fecha": fecha.isoformat(),
                "total_ingresos": total_ingresos,
                "por_metodo_pago": por_metodo,
                "cantidad_pagos": pagos_del_dia.count(),
                "total_anulado": total_anulado,
                "cantidad_anulados": anulados_del_dia.count(),
            },
            message="Resumen de caja calculado correctamente",
        )
