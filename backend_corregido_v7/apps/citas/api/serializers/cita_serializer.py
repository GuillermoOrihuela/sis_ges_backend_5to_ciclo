from datetime import datetime, timedelta
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from ...models.cita import Cita, DetalleCita
from ...services.cita_service import CitaService
from apps.servicios.models.servicio import Servicio

class DetalleCitaSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.ReadOnlyField(source='servicio.nombre')

    class Meta:
        model = DetalleCita
        fields = ['id', 'servicio', 'servicio_nombre', 'precio', 'duracion_minutos']

class CitaSerializer(serializers.ModelSerializer):
    detalles = DetalleCitaSerializer(many=True, read_only=True)
    cliente_nombres = serializers.ReadOnlyField(source='cliente.nombres')
    cliente_apellidos = serializers.ReadOnlyField(source='cliente.apellidos')
    cliente_telefono = serializers.ReadOnlyField(source='cliente.telefono')
    especialista_nombre = serializers.ReadOnlyField(source='especialista.nombres')
    # Solo-escritura: lista de IDs de Servicio para crear/reemplazar los
    # detalles de la cita. No existía forma de enviar esto antes (el único
    # campo relacionado, 'detalles', era read-only), así que crear una cita
    # desde el panel de gestión no permitía elegir servicios.
    servicios = serializers.PrimaryKeyRelatedField(
        queryset=Servicio.objects.filter(activo=True),
        many=True,
        write_only=True,
        required=True,
        help_text="IDs de los servicios de la cita. Se usan para calcular hora_fin y los detalles históricos.",
    )

    class Meta:
        model = Cita
        fields = [
            'id', 'cliente', 'cliente_nombres', 'cliente_apellidos', 'cliente_telefono',
            'especialista', 'especialista_nombre', 'fecha', 'hora_inicio',
            'hora_fin', 'estado', 'observaciones', 'codigo_reserva',
            'detalles', 'servicios', 'created_at', 'updated_at'
        ]
        # 'estado' es de solo lectura aquí: los cambios de estado deben pasar
        # por las acciones dedicadas (/confirmar, /cancelar, /iniciar,
        # /finalizar, /no-asistio), que sí validan la máquina de estados.
        # Antes se podía hacer PATCH {"estado": "FINALIZADA"} sin ninguna
        # validación de transición.
        read_only_fields = ['id', 'codigo_reserva', 'hora_fin', 'estado', 'created_at', 'updated_at']

    def create(self, validated_data):
        servicios = validated_data.pop('servicios')
        try:
            return CitaService.crear_cita_gestion(
                cliente=validated_data['cliente'],
                especialista=validated_data['especialista'],
                fecha=validated_data['fecha'],
                hora_inicio_str=validated_data['hora_inicio'],
                servicios_ids=[s.id for s in servicios],
                observaciones=validated_data.get('observaciones'),
            )
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                exc.message if hasattr(exc, 'message') else exc.messages
            )

    def update(self, instance, validated_data):
        # Si se envían servicios nuevos, se recalculan hora_fin y detalles;
        # si no, se actualizan solo los demás campos editables (fecha,
        # hora_inicio, especialista, observaciones, etc.) sin tocar detalles.
        servicios = validated_data.pop('servicios', None)
        if servicios is not None:
            duracion_total = sum(s.duracion_minutos for s in servicios)
            hora_inicio = validated_data.get('hora_inicio', instance.hora_inicio)
            dummy = datetime.combine(datetime.today(), hora_inicio if hasattr(hora_inicio, 'hour') else instance.hora_inicio)
            instance.hora_fin = (dummy + timedelta(minutes=duracion_total)).time()

            instance.detalles.all().delete()
            for servicio in servicios:
                DetalleCita.objects.create(
                    cita=instance, servicio=servicio,
                    precio=servicio.precio, duracion_minutos=servicio.duracion_minutos,
                )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class ReservaPublicaSerializer(serializers.Serializer):
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    telefono = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False, allow_blank=True)
    fecha = serializers.DateField()
    hora_inicio = serializers.CharField(max_length=10)
    especialista_id = serializers.IntegerField()
    servicios = serializers.ListField(child=serializers.IntegerField(), min_length=1)