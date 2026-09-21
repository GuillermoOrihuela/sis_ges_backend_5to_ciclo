from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ...models.usuario import Usuario
from ..serializers.usuario_serializer import UsuarioSerializer, MeSerializer
from common.api.mixins import ApiResponseMixin
from common.api.responses import APIResponse
from common.permissions.base import role_permission


class UsuarioViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    Gestión de usuarios del sistema. Restringida a ADMINISTRADOR/GERENTE en
    todas las acciones (a diferencia de otros módulos, aquí no tiene sentido
    dejar 'list'/'retrieve' abiertos a cualquier autenticado: expondría
    datos de cuentas de todo el personal).
    """
    queryset = Usuario.objects.all().order_by('username')
    serializer_class = UsuarioSerializer
    permission_classes = [role_permission('ADMINISTRADOR', 'GERENTE')]

    def perform_destroy(self, instance):
        # No permitir que un admin se elimine a sí mismo por error y quede
        # el sistema sin usuarios administrables.
        if instance.id == self.request.user.id:
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError("No puedes eliminar tu propio usuario.")
        instance.delete()


class MeAPIView(APIView):
    """GET /api/v1/auth/me/ — perfil del usuario autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return APIResponse.success(data=serializer.data, message="Perfil obtenido correctamente")
