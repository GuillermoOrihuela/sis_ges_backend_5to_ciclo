from django.db import models
from apps.servicios.models import Servicio
from .producto import Producto

class ConsumoServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='consumos_productos')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='servicios_consumidores')
    cantidad_estimada = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.servicio.nombre} consume {self.cantidad_estimada} de {self.producto.nombre}"

    class Meta:
        verbose_name = "Consumo de Servicio"
        verbose_name_plural = "Consumos de Servicios"

