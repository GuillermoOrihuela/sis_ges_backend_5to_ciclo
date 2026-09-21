from rest_framework import serializers
from ...models.cliente import Cliente

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id', 'nombres', 'apellidos', 'telefono', 
            'email', 'fecha_nacimiento', 'observaciones', 
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']