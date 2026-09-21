from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from ...models.servicio import Servicio, CategoriaServicio
from ..serializers.servicio_serializer import ServicioSerializer, CategoriaServicioSerializer
from common.api.mixins import ApiResponseMixin
from common.permissions.base import role_permission

class ServicioPublicoViewSet(ApiResponseMixin, viewsets.ReadOnlyModelViewSet):
    """Endpoint público para listar servicios activos (Contrato 33)"""
    queryset = Servicio.objects.filter(activo=True)
    serializer_class = ServicioSerializer
    permission_classes = [AllowAny]

class ServicioGestionViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """Gestión interna de servicios"""
    queryset = Servicio.objects.all().order_by('-created_at')
    serializer_class = ServicioSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()


class CategoriaServicioViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    Gestión de categorías de servicio (antes tenía serializer pero ningún
    endpoint la exponía; solo se podía administrar por Django Admin).
    """
    queryset = CategoriaServicio.objects.all().order_by('nombre')
    serializer_class = CategoriaServicioSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()