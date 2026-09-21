from django.db import models
from apps.clientes.models import Cliente
from apps.personal.models import Empleado
from apps.citas.models import Cita

class EstadoVenta(models.TextChoices):
    BORRADOR = 'BORRADOR', 'Borrador'
    CONFIRMADA = 'CONFIRMADA', 'Confirmada'
    ANULADA = 'ANULADA', 'Anulada'

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, null=True, blank=True, related_name='ventas')
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='ventas_realizadas')
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas')
    fecha = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=EstadoVenta.choices, default=EstadoVenta.BORRADOR)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Venta #{self.id} - Total: {self.total}"

    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"