from django.db import models
from apps.personal.models import Empleado
from apps.ventas.models import Venta, DetalleVenta

class EstadoComision(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADA = 'APROBADA', 'Aprobada'
    PAGADA = 'PAGADA', 'Pagada'
    ANULADA = 'ANULADA', 'Anulada'

class Comision(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='comisiones')
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='comisiones')
    detalle_venta = models.ForeignKey(DetalleVenta, on_delete=models.CASCADE, null=True, blank=True, related_name='comisiones')
    monto_base = models.DecimalField(max_digits=12, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=10.00) # Porcentaje estándar por defecto
    monto_comision = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=EstadoComision.choices, default=EstadoComision.PENDIENTE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comisión #{self.id} - Empleado {self.empleado} - {self.monto_comision}"

    class Meta:
        verbose_name = "Comisión"
        verbose_name_plural = "Comisiones"