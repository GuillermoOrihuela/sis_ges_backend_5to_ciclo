from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from ...models.comision import Comision
from ...services import comision_service
from ..serializers.comision_serializer import ComisionSerializer
from common.api.mixins import ApiResponseMixin
from common.api.responses import APIResponse
from common.permissions.base import role_permission


class ComisionViewSet(ApiResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Solo lectura por defecto (ver nota en el serializer). Aprobar/pagar/
    anular una comisión son operaciones financieras: restringidas a
    ADMINISTRADOR/GERENTE.
    """
    queryset = Comision.objects.select_related('empleado', 'venta').all().order_by('-created_at')
    serializer_class = ComisionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['empleado', 'estado', 'venta']

    def get_permissions(self):
        if self.action in ('aprobar', 'pagar', 'anular'):
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()

    def _transicion(self, pk, metodo_servicio, mensaje_ok):
        try:
            comision = metodo_servicio(pk)
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(comision)
        return APIResponse.success(data=serializer.data, message=mensaje_ok)

    def aprobar(self, request, pk=None):
        return self._transicion(pk, comision_service.aprobar_comision, "Comisión aprobada correctamente")

    def pagar(self, request, pk=None):
        return self._transicion(pk, comision_service.registrar_pago_comision, "Comisión pagada correctamente")

    def anular(self, request, pk=None):
        return self._transicion(pk, comision_service.anular_comision, "Comisión anulada correctamente")
