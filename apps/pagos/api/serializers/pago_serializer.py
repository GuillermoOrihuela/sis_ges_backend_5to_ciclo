from rest_framework import serializers
from ...models.pago import Pago


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            'id', 'venta', 'monto', 'metodo_pago', 'estado',
            'referencia', 'fecha', 'registrado_por', 'created_at',
        ]
        read_only_fields = ['id', 'estado', 'fecha', 'registrado_por', 'created_at']


class RegistrarPagoSerializer(serializers.Serializer):
    """Input de POST /gestion/pagos/ — se procesa con PagoService.registrar_pago
    para validar el saldo pendiente de la venta antes de crear el registro."""
    venta = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = serializers.CharField(max_length=30)
    referencia = serializers.CharField(required=False, allow_blank=True)
