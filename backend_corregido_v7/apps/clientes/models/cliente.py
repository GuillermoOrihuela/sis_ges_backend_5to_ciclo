from django.db import models
from common.utils.phone import normalizar_telefono

class Cliente(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Normaliza el teléfono antes de guardar, para que dos clientes
        # que ingresan el mismo número con distinto formato ("+51 999 999 999"
        # vs "999999999") se traten como el mismo cliente (ver CitaService,
        # regla de "una cita activa por día").
        if self.telefono:
            self.telefono = normalizar_telefono(self.telefono)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.telefono})"

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'