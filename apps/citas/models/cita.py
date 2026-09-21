from django.db import models
from apps.clientes.models.cliente import Cliente
from apps.personal.models.empleado import Empleado
from apps.servicios.models.servicio import Servicio

class EstadoCita(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    CONFIRMADA = 'CONFIRMADA', 'Confirmada'
    EN_PROCESO = 'EN_PROCESO', 'En Proceso'
    FINALIZADA = 'FINALIZADA', 'Finalizada'
    CANCELADA = 'CANCELADA', 'Cancelada'
    NO_ASISTIO = 'NO_ASISTIO', 'No Asistió'

class Cita(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='citas')
    especialista = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='citas')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(max_length=20, choices=EstadoCita.choices, default=EstadoCita.PENDIENTE)
    observaciones = models.TextField(blank=True, null=True)
    codigo_reserva = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cita #{self.codigo_reserva} - {self.cliente} ({self.fecha} {self.hora_inicio})"

    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'

class DetalleCita(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE, related_name='detalles')
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio histórico al reservar")
    duracion_minutos = models.PositiveIntegerField(help_text="Duración histórica en minutos")

    def __str__(self):
        return f"Detalle Cita #{self.cita.codigo_reserva} - {self.servicio.nombre}"