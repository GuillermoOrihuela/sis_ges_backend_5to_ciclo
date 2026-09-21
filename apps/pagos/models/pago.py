from django.db import models
from apps.ventas.models import Venta
from apps.usuarios.models import Usuario

class MetodoPago(models.TextChoices):
    EFECTIVO = 'EFECTIVO', 'Efectivo'
    TARJETA = 'TARJETA', 'Tarjeta'
    TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
    YAPE = 'YAPE', 'Yape'
    PLIN = 'PLIN', 'Plin'
    OTRO = 'OTRO', 'Otro'

class EstadoPago(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    PARCIAL = 'PARCIAL', 'Parcial'
    PAGADO = 'PAGADO', 'Pagado'
    ANULADO = 'ANULADO', 'Anulado'
    REEMBOLSADO = 'REEMBOLSADO', 'Reembolsado'

class Pago(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(max_length=30, choices=MetodoPago.choices)
    estado = models.CharField(max_length=30, choices=EstadoPago.choices, default=EstadoPago.PAGADO)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago #{self.id} - Venta #{self.venta.id} - {self.monto} ({self.metodo_pago})"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"