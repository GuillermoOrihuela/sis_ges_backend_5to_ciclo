from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

from apps.personal.models.empleado import Empleado, HorarioEmpleado, AusenciaEmpleado
from ..models.cita import Cita, EstadoCita

PASO_MINUTOS_DEFAULT = 15
DURACION_MINUTOS_DEFAULT = 30

ESTADOS_OCUPAN_AGENDA = [EstadoCita.PENDIENTE, EstadoCita.CONFIRMADA, EstadoCita.EN_PROCESO]


def _time_to_minutes(t):
    return t.hour * 60 + t.minute


def _minutes_to_str(m):
    return f"{m // 60:02d}:{m % 60:02d}"


class DisponibilidadService:
    @staticmethod
    def calcular(especialista_id, fecha, duracion_minutos=None, paso_minutos=PASO_MINUTOS_DEFAULT):
        """
        Calcula los horarios de inicio disponibles para un especialista en una
        fecha dada, considerando:
        - su horario laboral configurado para ese día de la semana,
        - sus ausencias (vacaciones, permisos, etc.) que cubran esa fecha,
        - las citas ya activas (PENDIENTE/CONFIRMADA/EN_PROCESO) ese día.
        """
        try:
            especialista = Empleado.objects.get(id=especialista_id, activo=True)
        except Empleado.DoesNotExist:
            raise ValidationError("El especialista seleccionado no existe o no está activo.")

        duracion_minutos = duracion_minutos or DURACION_MINUTOS_DEFAULT
        if duracion_minutos <= 0:
            raise ValidationError("duracion_minutos debe ser un número positivo.")

        # dia_semana: 0 = Lunes ... 6 = Domingo, igual que date.weekday()
        dia_semana = fecha.weekday()

        horario = HorarioEmpleado.objects.filter(
            empleado=especialista, dia_semana=dia_semana, activo=True
        ).first()

        if horario is None:
            return {
                "especialista_id": especialista.id,
                "fecha": fecha.isoformat(),
                "horario_laboral": None,
                "motivo_sin_horario": "El especialista no tiene un horario laboral configurado para ese día.",
                "duracion_minutos": duracion_minutos,
                "slots_disponibles": [],
            }

        ausencia = AusenciaEmpleado.objects.filter(
            empleado=especialista, fecha_inicio__lte=fecha, fecha_fin__gte=fecha
        ).first()

        if ausencia is not None:
            return {
                "especialista_id": especialista.id,
                "fecha": fecha.isoformat(),
                "horario_laboral": {
                    "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                    "hora_fin": horario.hora_fin.strftime("%H:%M"),
                },
                "motivo_sin_horario": f"El especialista está ausente ese día (motivo: {ausencia.motivo}).",
                "duracion_minutos": duracion_minutos,
                "slots_disponibles": [],
            }

        # Intervalos ocupados por citas activas ese día.
        citas_del_dia = Cita.objects.filter(
            especialista=especialista, fecha=fecha, estado__in=ESTADOS_OCUPAN_AGENDA
        )
        ocupados = [
            (_time_to_minutes(c.hora_inicio), _time_to_minutes(c.hora_fin))
            for c in citas_del_dia
        ]

        inicio_jornada = _time_to_minutes(horario.hora_inicio)
        fin_jornada = _time_to_minutes(horario.hora_fin)

        slots = []
        cursor = inicio_jornada
        while cursor + duracion_minutos <= fin_jornada:
            slot_fin = cursor + duracion_minutos
            se_cruza = any(cursor < fin_o and slot_fin > inicio_o for inicio_o, fin_o in ocupados)
            if not se_cruza:
                slots.append(_minutes_to_str(cursor))
            cursor += paso_minutos

        return {
            "especialista_id": especialista.id,
            "fecha": fecha.isoformat(),
            "horario_laboral": {
                "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
                "hora_fin": horario.hora_fin.strftime("%H:%M"),
            },
            "motivo_sin_horario": None,
            "duracion_minutos": duracion_minutos,
            "slots_disponibles": slots,
        }
