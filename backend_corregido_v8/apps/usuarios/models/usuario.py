from django.contrib.auth.models import AbstractUser
from django.db import models
from .rol import RolUsuario
from .managers import UsuarioManager

class Usuario(AbstractUser):
    rol = models.CharField(
        max_length=30,
        choices=RolUsuario.choices,
        default=RolUsuario.RECEPCIONISTA
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)

    objects = UsuarioManager()

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_custom_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_custom_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user_permissions',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"