from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from ...models.empleado import Empleado, Turno, HorarioEmpleado, AusenciaEmpleado
from ..serializers.empleado_serializer import (
    EmpleadoSerializer, TurnoSerializer, HorarioEmpleadoSerializer, AusenciaEmpleadoSerializer
)
from common.api.mixins import ApiResponseMixin
from common.permissions.base import role_permission

class EmpleadoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = Empleado.objects.all().order_by('-created_at')
    serializer_class = EmpleadoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()

class EspecialistaPublicoViewSet(ApiResponseMixin, viewsets.ReadOnlyModelViewSet):
    """
    Endpoint público obligatorio para listar especialistas (Contrato 33).

    Nota: usa el mismo EmpleadoSerializer que la gestión interna, por lo que
    expone también el campo `usuario` (FK al usuario del sistema vinculado).
    Si se necesita un serializer público "recortado" (sin `usuario`), pedir
    que se cree uno específico — se dejó fuera de este arreglo para no
    cambiar el contrato de datos sin confirmación explícita.
    """
    queryset = Empleado.objects.filter(activo=True)
    serializer_class = EmpleadoSerializer
    permission_classes = [AllowAny]

class TurnoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """
    Catálogo de turnos (nombre + rango horario). Como 'nombre' ya no es
    único ni está limitado a un enum fijo (ver migración
    0002_turnos_horarios_flexibles), cualquier usuario autenticado puede
    crear los turnos que su negocio necesite.
    """
    queryset = Turno.objects.all().order_by('nombre')
    serializer_class = TurnoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activo']

    def get_permissions(self):
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()

class HorarioEmpleadoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = HorarioEmpleado.objects.select_related('turno').all().order_by('empleado', 'dia_semana', 'hora_inicio')
    serializer_class = HorarioEmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['empleado', 'dia_semana', 'turno', 'activo']

class AusenciaEmpleadoViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    queryset = AusenciaEmpleado.objects.all().order_by('-fecha_inicio')
    serializer_class = AusenciaEmpleadoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['empleado']