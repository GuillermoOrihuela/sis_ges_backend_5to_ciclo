from django.db import models
from .categoria import CategoriaProducto

class Producto(models.Model):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"