from rest_framework import serializers
from ...models.comision import Comision


class ComisionSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Comision
        fields = [
            'id', 'empleado', 'empleado_nombre', 'venta', 'detalle_venta',
            'monto_base', 'porcentaje', 'monto_comision', 'estado',
            'created_at', 'updated_at',
        ]
        read_only_fields = fields
        # Las comisiones se generan automáticamente al confirmar una venta
        # (VentaService.confirmar_venta -> generar_comisiones_venta), así
        # que este endpoint es de solo lectura salvo por las acciones
        # dedicadas de cambio de estado (/aprobar, /pagar, /anular).

    def get_empleado_nombre(self, obj):
        return f"{obj.empleado.nombres} {obj.empleado.apellidos}"
