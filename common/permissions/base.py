"""
Permisos base compartidos.

El sistema de permisos combina Django Permissions con permisos
personalizados cuando sea necesario (sección 16). No crear sistemas
paralelos de permisos: los permisos por rol deben construirse a partir de
`role_permission()` para mantener un único mecanismo consistente.

Los roles oficiales están definidos en el modelo Usuario (sección 5):
ADMINISTRADOR, GERENTE, RECEPCIONISTA, ESPECIALISTA, VENDEDOR.
"""
from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Permiso base: permite el acceso solo si el usuario autenticado tiene
    uno de los roles listados en `allowed_roles`. No instanciar
    directamente; usar `role_permission(*roles)` para generar una subclase.
    """

    allowed_roles = ()
    message = "No tiene el rol requerido para realizar esta acción."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not (user and user.is_authenticated):
            return False
        # Un superusuario de Django (is_superuser=True) siempre pasa,
        # independientemente de su campo 'rol'. Esto evita quedar
        # bloqueado del propio sistema: `createsuperuser` no pregunta por
        # campos personalizados como 'rol' (no está en REQUIRED_FIELDS),
        # así que el primer superusuario creado quedaba con el valor por
        # defecto (RECEPCIONISTA) y no podía gestionar ni siquiera usuarios.
        if user.is_superuser:
            return True
        return getattr(user, "rol", None) in self.allowed_roles


def role_permission(*roles):
    """
    Genera dinámicamente una clase de permiso DRF que exige que el usuario
    tenga alguno de los roles indicados.

    Ejemplo:
        class CitaViewSet(viewsets.ModelViewSet):
            permission_classes = [role_permission("ADMINISTRADOR", "RECEPCIONISTA")]
    """
    class_name = "RolePermission_" + "_".join(roles)
    return type(class_name, (HasRole,), {"allowed_roles": tuple(roles)})


class IsOwnerOrReadOnly(BasePermission):
    """
    Permiso genérico de ejemplo: solo el dueño del objeto puede modificarlo;
    cualquier usuario autenticado puede leerlo. Requiere que el modelo
    tenga un campo `usuario` o `empleado` apuntando al request.user.
    """

    owner_field = "usuario"

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return getattr(obj, self.owner_field, None) == request.user
