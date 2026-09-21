"""
Modelos base abstractos.

La mayoría de los modelos oficiales del contrato (Cliente, Servicio,
Empleado, Producto, etc.) comparten los campos created_at/updated_at, y
muchos también un campo `activo`. Heredar de estas clases evita duplicar
esos campos en cada app.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Agrega created_at / updated_at automáticos."""

    created_at = models.DateTimeField("Fecha de creación", auto_now_add=True)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        abstract = True


class ActivableModel(models.Model):
    """Agrega el campo `activo`, usado para soft-disable en varios modelos."""

    activo = models.BooleanField("Activo", default=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, ActivableModel):
    """Combinación de timestamps + activo, para modelos catálogo típicos
    (Servicio, Producto, CategoriaProducto, etc.). No todos los modelos del
    contrato usan `activo` (p. ej. Cita no lo usa) — heredar solo cuando
    corresponda; en caso contrario usar TimeStampedModel a secas."""

    class Meta:
        abstract = True
