from django.db import models
from django.conf import settings

class Empleado(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='empleado_perfil'
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.cargo}"

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'


class TurnoEnum(models.TextChoices):
    """
    Turnos de referencia sugeridos (se siguen pudiendo usar como guía en el
    formulario del frontend), pero YA NO restringen qué se puede crear:
    antes 'nombre' sólo aceptaba uno de estos 3 valores y encima era
    unique=True, así que en todo el sistema sólo podían existir 3 turnos en
    total, compartidos por todos los empleados. Como cada negocio/empleado
    puede tener turnos con nombres y horarios propios ("Turno Fin de
    Semana", "Turno Nocturno", "Turno de Juan"), 'nombre' pasó a ser texto
    libre (ver Turno.nombre más abajo).
    """
    MANANA = 'MANANA', 'Mañana'
    TARDE = 'TARDE', 'Tarde'
    NOCHE = 'NOCHE', 'Noche'
    COMPLETO = 'COMPLETO', 'Completo'
    FIN_DE_SEMANA = 'FIN_DE_SEMANA', 'Fin de semana'


class Turno(models.Model):
    nombre = models.CharField(max_length=50)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class HorarioEmpleado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.IntegerField(help_text="0: Lunes, 6: Domingo")
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT)
    activo = models.BooleanField(default=True)

    class Meta:
        # Antes: unique_together = ('empleado', 'dia_semana') impedía que un
        # empleado tuviera más de un horario el mismo día — o sea, ningún
        # turno partido (mañana + tarde con descanso al mediodía) ni
        # horarios que varíen de una semana a otra sin borrar el anterior.
        # Se quitó esa restricción; ahora la validación real (que no se
        # superpongan los rangos de hora) vive en
        # HorarioEmpleadoSerializer.validate(), que sí permite varios
        # horarios no solapados el mismo día.
        verbose_name = 'Horario de Empleado'
        verbose_name_plural = 'Horarios de Empleados'


class AusenciaEmpleado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='ausencias')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ausencia de Empleado'
        verbose_name_plural = 'Ausencias de Empleados'