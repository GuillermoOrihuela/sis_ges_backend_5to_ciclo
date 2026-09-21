from rest_framework import serializers
from ...models import (
    CategoriaProducto, Producto, Almacen, Existencia,
    MovimientoInventario, TipoMovimientoInventario,
)


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = ['id', 'nombre', 'descripcion', 'activo']


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ['id', 'nombre', 'ubicacion', 'activo']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')
    # Suma de stock en todos los almacenes; útil para listados sin tener que
    # pedir aparte /gestion/existencias/ y cruzar por producto.
    stock_total = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'categoria', 'categoria_nombre', 'nombre', 'descripcion',
            'codigo', 'precio_venta', 'activo', 'stock_total',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_stock_total(self, obj):
        from django.db.models import Sum
        return obj.existencias.aggregate(total=Sum('stock_actual'))['total'] or 0


class ExistenciaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    almacen_nombre = serializers.ReadOnlyField(source='almacen.nombre')

    class Meta:
        model = Existencia
        fields = [
            'id', 'producto', 'producto_nombre', 'almacen', 'almacen_nombre',
            'stock_actual', 'stock_minimo', 'updated_at',
        ]
        read_only_fields = ['id', 'stock_actual', 'updated_at']
        # stock_actual es de solo lectura a propósito: solo debe cambiar a
        # través de un MovimientoInventario (que además deja registro en
        # Kardex). Editarlo a mano aquí rompería la trazabilidad.


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.ReadOnlyField(source='producto.nombre')
    almacen_nombre = serializers.ReadOnlyField(source='almacen.nombre')

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'producto', 'producto_nombre', 'almacen', 'almacen_nombre',
            'tipo_movimiento', 'cantidad', 'stock_anterior', 'stock_posterior',
            'motivo', 'registrado_por', 'created_at',
        ]
        read_only_fields = ['id', 'stock_anterior', 'stock_posterior', 'registrado_por', 'created_at']


class RegistrarMovimientoSerializer(serializers.Serializer):
    """Input para POST /gestion/movimientos-inventario/ (crea vía servicio, no ModelSerializer.create)."""
    producto = serializers.IntegerField()
    almacen = serializers.IntegerField()
    tipo_movimiento = serializers.ChoiceField(choices=TipoMovimientoInventario.choices)
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2)
    motivo = serializers.CharField(required=False, allow_blank=True)
