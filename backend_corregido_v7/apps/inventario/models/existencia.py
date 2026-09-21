from django.db import models
from .producto import Producto
from .almacen import Almacen

class Existencia(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='existencias')
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name='existencias')
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} en {self.almacen.nombre}: {self.stock_actual}"

    class Meta:
        verbose_name = "Existencia"
        verbose_name_plural = "Existencias"
        constraints = [
            models.UniqueConstraint(fields=['producto', 'almacen'], name='unique_producto_almacen')
        ]