from django.db import models
from .producto import Producto
from .almacen import Almacen
from apps.usuarios.models import Usuario

class TipoMovimientoInventario(models.TextChoices):
    ENTRADA = 'ENTRADA', 'Entrada'
    SALIDA = 'SALIDA', 'Salida'
    AJUSTE_POSITIVO = 'AJUSTE_POSITIVO', 'Ajuste Positivo'
    AJUSTE_NEGATIVO = 'AJUSTE_NEGATIVO', 'Ajuste Negativo'
    VENTA = 'VENTA', 'Venta'
    CONSUMO_SERVICIO = 'CONSUMO_SERVICIO', 'Consumo por Servicio'
    DEVOLUCION = 'DEVOLUCION', 'Devolución'

class MovimientoInventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='movimientos')
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=30, choices=TipoMovimientoInventario.choices)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    stock_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    stock_posterior = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.TextField(blank=True, null=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre} ({self.cantidad})"

    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"

class Kardex(models.Model):
    movimiento = models.OneToOneField(MovimientoInventario, on_delete=models.CASCADE, related_name='kardex')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='kardex')
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name='kardex')
    fecha = models.DateTimeField(auto_now_add=True)
    stock_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    stock_final = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_movimiento = models.CharField(max_length=30, choices=TipoMovimientoInventario.choices)

    def __str__(self):
        return f"Kardex #{self.id} - {self.producto.nombre}"

    class Meta:
        verbose_name = "Kardex"
        verbose_name_plural = "Kardex"