from rest_framework import serializers
from ...models.servicio import Servicio, CategoriaServicio

class CategoriaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaServicio
        fields = ['id', 'nombre', 'descripcion', 'activo']

class ServicioSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Servicio
        fields = [
            'id', 'categoria', 'categoria_nombre', 'nombre', 
            'descripcion', 'duracion_minutos', 'precio', 
            'activo', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']