from django.contrib.auth.models import UserManager


class UsuarioManager(UserManager):
    """
    UserManager estándar de Django, con un único ajuste: al crear un
    superusuario (`createsuperuser` / `create_superuser(...)`), asigna
    automáticamente rol=ADMINISTRADOR si el caller no especificó uno.
    Sin esto, 'rol' quedaba en su valor por defecto (RECEPCIONISTA) porque
    no está en REQUIRED_FIELDS y el comando no pregunta por él.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('rol', 'ADMINISTRADOR')
        return super().create_superuser(username, email=email, password=password, **extra_fields)
