from django.db import models

class RolUsuario(models.TextChoices):
    ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'
    GERENTE = 'GERENTE', 'Gerente'
    RECEPCIONISTA = 'RECEPCIONISTA', 'Recepcionista'
    ESPECIALISTA = 'ESPECIALISTA', 'Especialista'
    VENDEDOR = 'VENDEDOR', 'Vendedor'