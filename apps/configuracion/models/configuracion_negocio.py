from django.db import models

class ConfiguracionNegocio(models.Model):
    nombre_negocio = models.CharField(max_length=150, default="Salón de Manicure")
    horario_apertura = models.TimeField(default="09:00:00")
    horario_cierre = models.TimeField(default="20:00:00")
    duracion_minima_intervalo = models.IntegerField(default=30) # en minutos
    politica_cancelacion_horas = models.IntegerField(default=2)
    porcentaje_comision_default = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración General - {self.nombre_negocio}"

    class Meta:
        verbose_name = "Configuración del Negocio"
        verbose_name_plural = "Configuraciones del Negocio"