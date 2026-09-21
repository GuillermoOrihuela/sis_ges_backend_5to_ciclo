from rest_framework import serializers
from ...models.usuario import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Gestión de usuarios del sistema (alta/baja/edición, asignación de rol).
    Antes no existía ningún endpoint para esto (ver INTEGRACION_BACKEND.md,
    punto 11) — el panel de "Usuarios" solo podía administrarse por Django
    Admin.
    """
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    empleado_id = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email', 'telefono',
            'rol', 'is_active', 'empleado_id', 'password', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']

    def get_empleado_id(self, obj):
        empleado = getattr(obj, 'empleado_perfil', None)
        return empleado.id if empleado else None

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "La contraseña es obligatoria al crear un usuario."})
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    """
    Respuesta de GET /api/v1/auth/me/ (resuelve INTEGRACION_BACKEND.md,
    punto 3): expone lo mínimo que el frontend necesita para mostrar
    permisos reales por rol y vincular al Empleado del usuario logueado.
    """
    empleado_id = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'empleado_id']

    def get_empleado_id(self, obj):
        empleado = getattr(obj, 'empleado_perfil', None)
        return empleado.id if empleado else None
