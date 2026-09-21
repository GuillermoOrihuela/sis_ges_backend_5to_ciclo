from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ...models import CategoriaProducto, Producto, Almacen, Existencia, MovimientoInventario
from ...services.inventario_service import registrar_movimiento_inventario
from ..serializers.inventario_serializer import (
    CategoriaProductoSerializer, ProductoSerializer, AlmacenSerializer,
    ExistenciaSerializer, MovimientoInventarioSerializer, RegistrarMovimientoSerializer,
)
from common.api.mixins import ApiResponseMixin
from common.api.responses import APIResponse
from common.permissions.base import role_permission


class CategoriaProductoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    serializer_class = CategoriaProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()


class AlmacenViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = Almacen.objects.all().order_by('nombre')
    serializer_class = AlmacenSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()


class ProductoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()


class ExistenciaViewSet(ApiResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Solo lectura: el stock nunca se edita directamente (ver nota en el
    serializer); para modificarlo hay que pasar por
    POST /gestion/movimientos-inventario/.
    """
    queryset = Existencia.objects.select_related('producto', 'almacen').all()
    serializer_class = ExistenciaSerializer
    permission_classes = [IsAuthenticated]


class MovimientoInventarioViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    'list'/'retrieve' devuelven el historial (Kardex resumido); 'create' NO
    usa el ModelSerializer por defecto — delega en
    inventario_service.registrar_movimiento_inventario para mantener
    stock/Kardex siempre consistentes. No se permite update/destroy: un
    movimiento de inventario es un hecho histórico, se corrige con un
    movimiento inverso, no editándolo.
    """
    queryset = MovimientoInventario.objects.select_related('producto', 'almacen').all().order_by('-created_at')
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        input_serializer = RegistrarMovimientoSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            movimiento = registrar_movimiento_inventario(
                producto_id=data['producto'],
                almacen_id=data['almacen'],
                tipo_movimiento=data['tipo_movimiento'],
                cantidad=data['cantidad'],
                registrado_por=request.user,
                motivo=data.get('motivo'),
            )
        except ValidationError as e:
            return APIResponse.error(
                message=str(e.message if hasattr(e, 'message') else e.args[0]),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = self.get_serializer(movimiento)
        return APIResponse.success(
            data=output_serializer.data,
            message="Movimiento de inventario registrado correctamente",
            status_code=status.HTTP_201_CREATED,
        )
