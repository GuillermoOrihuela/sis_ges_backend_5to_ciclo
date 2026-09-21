from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from ...models.cita import Cita
from ...services.cita_service import CitaService
from ...services.disponibilidad_service import DisponibilidadService
from ..serializers.cita_serializer import CitaSerializer, ReservaPublicaSerializer
from ..filters.cita_filter import CitaFilter
from common.api.responses import APIResponse
from common.api.mixins import ApiResponseMixin
from common.permissions.base import role_permission

class ReservaPublicaAPIView(APIView):
    """Endpoint público obligatorio de reserva sin JWT (Contratos 10 y 33)"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ReservaPublicaSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message="Error de validación en la reserva", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        try:
            cita = CitaService.crear_reserva_publica(serializer.validated_data)
            response_serializer = CitaSerializer(cita)
            return APIResponse.success(data=response_serializer.data, message="Cita reservada exitosamente", status_code=status.HTTP_201_CREATED)
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)


class DisponibilidadPublicaAPIView(APIView):
    """
    Endpoint público de disponibilidad (Contrato 33).

    Query params:
      - especialista_id (obligatorio): id del Empleado
      - fecha (obligatorio): YYYY-MM-DD
      - duracion_minutos (opcional, default 30): duración del servicio a agendar
      - paso_minutos (opcional, default 15): granularidad de los horarios sugeridos
    """
    permission_classes = [AllowAny]

    def get(self, request):
        especialista_id = request.query_params.get('especialista_id')
        fecha_str = request.query_params.get('fecha')

        if not especialista_id or not fecha_str:
            return APIResponse.error(
                message="Los parámetros 'especialista_id' y 'fecha' son obligatorios.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return APIResponse.error(
                message="El parámetro 'fecha' debe tener el formato YYYY-MM-DD.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        duracion_minutos = request.query_params.get('duracion_minutos')
        paso_minutos = request.query_params.get('paso_minutos')

        try:
            resultado = DisponibilidadService.calcular(
                especialista_id=especialista_id,
                fecha=fecha,
                duracion_minutos=int(duracion_minutos) if duracion_minutos else None,
                paso_minutos=int(paso_minutos) if paso_minutos else 15,
            )
            return APIResponse.success(data=resultado, message="Disponibilidad calculada correctamente")
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)


class CitaGestionViewSet(ApiResponseMixin, viewsets.ModelViewSet):
    """Gestión interna de citas y transiciones de estado"""
    queryset = Cita.objects.all().order_by('-fecha', '-hora_inicio')
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CitaFilter

    def get_permissions(self):
        # Eliminar una cita es una operación sensible: se reserva a roles
        # con más responsabilidad. Cancelar (que conserva el historial) sí
        # sigue disponible para cualquier usuario autenticado vía /cancelar/.
        if self.action == 'destroy':
            return [role_permission('ADMINISTRADOR', 'GERENTE')()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save()

    # Acciones personalizadas para transiciones de estado oficiales (Contratos 12 y 33)
    def _ejecutar_transicion(self, request, pk, servicio_metodo):
        try:
            cita = servicio_metodo(pk)
            serializer = self.get_serializer(cita)
            return APIResponse.success(data=serializer.data, message="Estado de cita actualizado correctamente")
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

    def confirmar(self, request, pk=None):
        return self._ejecutar_transicion(request, pk, CitaService.confirmar_cita)

    def cancelar(self, request, pk=None):
        return self._ejecutar_transicion(request, pk, CitaService.cancelar_cita)

    def iniciar(self, request, pk=None):
        return self._ejecutar_transicion(request, pk, CitaService.iniciar_cita)

    def finalizar(self, request, pk=None):
        return self._ejecutar_transicion(request, pk, CitaService.finalizar_cita)

    def no_asistio(self, request, pk=None):
        return self._ejecutar_transicion(request, pk, CitaService.marcar_no_asistio)

    def reprogramar(self, request, pk=None):
        nueva_fecha = request.data.get('fecha')
        nueva_hora_inicio = request.data.get('hora_inicio')
        if not nueva_fecha or not nueva_hora_inicio:
            return APIResponse.error(
                message="Se requieren 'fecha' y 'hora_inicio' para reprogramar.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            cita = CitaService.reprogramar_cita(pk, nueva_fecha, nueva_hora_inicio)
            serializer = self.get_serializer(cita)
            return APIResponse.success(data=serializer.data, message="Cita reprogramada correctamente")
        except ValidationError as e:
            return APIResponse.error(message=str(e.message if hasattr(e, 'message') else e.args[0]), status_code=status.HTTP_400_BAD_REQUEST)
        except Cita.DoesNotExist:
            return APIResponse.error(message="La cita no existe.", status_code=status.HTTP_404_NOT_FOUND)