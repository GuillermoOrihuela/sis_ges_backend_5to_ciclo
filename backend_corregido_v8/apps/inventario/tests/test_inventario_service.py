from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.inventario.models import CategoriaProducto, Producto, Almacen, Existencia, TipoMovimientoInventario
from apps.inventario.services.inventario_service import registrar_movimiento_inventario

class InventarioServiceTestCase(TestCase):
    def setUp(self):
        self.categoria = CategoriaProducto.objects.create(nombre="Esmaltes")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Esmaltes Rojo",
            codigo="ESM-001",
            precio_venta=25.00
        )
        self.almacen = Almacen.objects.create(nombre="Principal")
        self.existencia = Existencia.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            stock_actual=10.00,
            stock_minimo=2.00
        )

    def test_registrar_entrada_inventario(self):
        movimiento = registrar_movimiento_inventario(
            producto_id=self.producto.id,
            almacen_id=self.almacen.id,
            tipo_movimiento=TipoMovimientoInventario.ENTRADA,
            cantidad=5.00,
            motivo="Compra de stock"
        )
        self.existencia.refresh_from_db()
        self.assertEqual(self.existencia.stock_actual, 15.00)
        self.assertEqual(movimiento.stock_posterior, 15.00)

    def test_error_stock_insufficiente(self):
        with self.assertRaises(ValidationError):
            registrar_movimiento_inventario(
                producto_id=self.producto.id,
                almacen_id=self.almacen.id,
                tipo_movimiento=TipoMovimientoInventario.SALIDA,
                cantidad=20.00, # Excede el stock actual de 10.00
                motivo="Salida excesiva"
            )