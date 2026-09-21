from django.db import models
from .venta import Venta
from apps.servicios.models import Servicio
from apps.inventario.models import Producto

class TipoItemVenta(models.TextChoices):
    SERVICIO = 'SERVICIO', 'Servicio'
    PRODUCTO = 'PRODUCTO', 'Producto'

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    tipo_item = models.CharField(max_length=20, choices=TipoItemVenta.choices)
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, null=True, blank=True, related_name='detalles_venta')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True, related_name='detalles_venta')
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Detalle #{self.id} - {self.descripcion} (x{self.cantidad})"

    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"