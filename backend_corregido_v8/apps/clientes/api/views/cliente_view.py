from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from ...models.cliente import Cliente
from ..serializers.cliente_serializer import ClienteSerializer
from ..filters.cliente_filter import ClienteFilter
from common.api.mixins import ApiResponseMixin
from common.permissions.base import role_permission

class ClienteViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by('-created_at')
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClienteFilter

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()