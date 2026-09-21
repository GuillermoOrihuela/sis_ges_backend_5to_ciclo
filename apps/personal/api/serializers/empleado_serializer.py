from rest_framework import serializers
from ...models.empleado import Empleado, Turno, HorarioEmpleado, AusenciaEmpleado

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = [
            'id', 'usuario', 'nombres', 'apellidos', 'telefono', 
            'fecha_ingreso', 'cargo', 'activo', 'created_at', 'updated_at'
        ]

class TurnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turno
        fields = ['id', 'nombre', 'hora_inicio', 'hora_fin', 'activo']

class HorarioEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioEmpleado
        fields = ['id', 'empleado', 'dia_semana', 'hora_inicio', 'hora_fin', 'turno', 'activo']

    def validate(self, attrs):
        # Ya no existe unique_together('empleado', 'dia_semana') a nivel de
        # base de datos (ver apps/personal/migrations/0002_...), así que un
        # empleado puede tener varios horarios el mismo día (turno partido:
        # mañana + tarde). Lo único que debe seguir sin permitirse es que
        # dos rangos de hora se superpongan para el mismo empleado y día.
        empleado = attrs.get('empleado', getattr(self.instance, 'empleado', None))
        dia_semana = attrs.get('dia_semana', getattr(self.instance, 'dia_semana', None))
        hora_inicio = attrs.get('hora_inicio', getattr(self.instance, 'hora_inicio', None))
        hora_fin = attrs.get('hora_fin', getattr(self.instance, 'hora_fin', None))

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise serializers.ValidationError({"hora_fin": "La hora de fin debe ser posterior a la hora de inicio."})

        if empleado and dia_semana is not None and hora_inicio and hora_fin:
            qs = HorarioEmpleado.objects.filter(empleado=empleado, dia_semana=dia_semana, activo=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            for existente in qs:
                si_solapa = hora_inicio < existente.hora_fin and hora_fin > existente.hora_inicio
                if si_solapa:
                    raise serializers.ValidationError(
                        f"Ya existe un horario para este empleado ese día entre "
                        f"{existente.hora_inicio.strftime('%H:%M')} y {existente.hora_fin.strftime('%H:%M')} "
                        f"que se superpone con el rango indicado."
                    )
        return attrs

class AusenciaEmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AusenciaEmpleado
        fields = ['id', 'empleado', 'fecha_inicio', 'fecha_fin', 'motivo', 'created_at']

    def validate(self, attrs):
        fecha_inicio = attrs.get('fecha_inicio', getattr(self.instance, 'fecha_inicio', None))
        fecha_fin = attrs.get('fecha_fin', getattr(self.instance, 'fecha_fin', None))
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return attrs