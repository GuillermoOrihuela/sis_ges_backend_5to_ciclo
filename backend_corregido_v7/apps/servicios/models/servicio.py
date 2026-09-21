from django.db import models

class CategoriaServicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    categoria = models.ForeignKey(CategoriaServicio, on_delete=models.PROTECT, related_name='servicios')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    duracion_minutos = models.PositiveIntegerField(help_text="Duración oficial en minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.duracion_minutos} min - S/ {self.precio})"

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'