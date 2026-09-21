from rest_framework import serializers
from ...models import Venta, DetalleVenta, TipoItemVenta


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'tipo_item', 'servicio', 'producto', 'descripcion',
            'cantidad', 'precio_unitario', 'descuento', 'subtotal',
        ]
        read_only_fields = ['id', 'descripcion', 'precio_unitario', 'subtotal']


class ItemVentaInputSerializer(serializers.Serializer):
    """Un ítem tal como lo arma el frontend al armar el carrito de una venta."""
    tipo_item = serializers.ChoiceField(choices=TipoItemVenta.choices)
    servicio = serializers.IntegerField(required=False, allow_null=True)
    producto = serializers.IntegerField(required=False, allow_null=True)
    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2, default=1)
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

    def validate(self, attrs):
        if attrs['tipo_item'] == TipoItemVenta.SERVICIO and not attrs.get('servicio'):
            raise serializers.ValidationError("Los ítems de tipo SERVICIO requieren 'servicio'.")
        if attrs['tipo_item'] == TipoItemVenta.PRODUCTO and not attrs.get('producto'):
            raise serializers.ValidationError("Los ítems de tipo PRODUCTO requieren 'producto'.")
        return attrs


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    empleado_nombre = serializers.ReadOnlyField(source='empleado.nombres')
    # Solo-escritura: los ítems que arma el carrito del frontend. Se procesan
    # en la vista con VentaService.crear_venta (no hay un create() aquí
    # porque la vista necesita orquestar servicios, no solo guardar campos).
    items = ItemVentaInputSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'cliente', 'cliente_nombre', 'empleado', 'empleado_nombre',
            'cita', 'fecha', 'subtotal', 'descuento', 'total', 'estado',
            'detalles', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'subtotal', 'total', 'estado', 'fecha', 'created_at', 'updated_at']

    def get_cliente_nombre(self, obj):
        if not obj.cliente:
            return None
        return f"{obj.cliente.nombres} {obj.cliente.apellidos}"
