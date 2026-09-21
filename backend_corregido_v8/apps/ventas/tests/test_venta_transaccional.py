from decimal import Decimal
from django.test import TestCase
from apps.clientes.models import Cliente
from apps.personal.models import Empleado
from apps.servicios.models.servicio import Servicio, CategoriaServicio
from apps.inventario.models import CategoriaProducto, Producto, Almacen, Existencia
from apps.ventas.services.venta_service import crear_venta, confirmar_venta
from apps.ventas.models import EstadoVenta, TipoItemVenta
from apps.comisiones.models import Comision, EstadoComision
from datetime import date

class VentaTransaccionalTestCase(TestCase):
    def setUp(self):
        self.categoria = CategoriaServicio.objects.create(nombre="Uñas")
        self.empleado = Empleado.objects.create(
            nombres="Ana",
            apellidos="Sánchez",
            telefono="955444333",
            cargo="ESPECIALISTA",
            fecha_ingreso=date.today(),
        )
        self.cliente = Cliente.objects.create(
            nombres="Rosa",
            apellidos="Meza",
            telefono="944333222"
        )
        self.servicio = Servicio.objects.create(
            nombre="Uñas Acrílicas",
            duracion_minutos=60,
            precio=80.00,
            categoria=self.categoria,
            activo=True
        )
        self.categoria = CategoriaProducto.objects.create(nombre="Insumos")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Acrílico en Polvo",
            codigo="ACR-01",
            precio_venta=40.00
        )
        self.almacen = Almacen.objects.create(nombre="Almacén Central")
        self.existencia = Existencia.objects.create(
            producto=self.producto,
            almacen=self.almacen,
            stock_actual=20.00,
            stock_minimo=5.00
        )

    def test_flujo_completo_venta_y_comision(self):
        items = [
            {
                "tipo_item": TipoItemVenta.SERVICIO,
                "servicio": self.servicio,
                "cantidad": 1,
                "precio_unitario": Decimal('80.00')
            },
            {
                "tipo_item": TipoItemVenta.PRODUCTO,
                "producto": self.producto,
                "cantidad": 2,
                "precio_unitario": Decimal('40.00')
            }
        ]

        # 1. Crear venta en borrador
        venta = crear_venta(empleado=self.empleado, items_data=items, cliente=self.cliente)
        self.assertEqual(venta.estado, EstadoVenta.BORRADOR)
        self.assertEqual(venta.total, Decimal('160.00'))

        # 2. Confirmar venta (debe descontar inventario y generar comisiones)
        venta_confirmada = confirmar_venta(venta.id, almacen_id=self.almacen.id)
        self.assertEqual(venta_confirmada.estado, EstadoVenta.CONFIRMADA)

        # Verificar descuento de inventario del producto
        self.existencia.refresh_from_db()
        self.assertEqual(self.existencia.stock_actual, 18.00) # 20 - 2

        # Verificar generación automática de comisión para el empleado sobre el servicio
        comisiones = Comision.objects.filter(venta=venta, empleado=self.empleado)
        self.assertEqual(comisiones.count(), 1)
        self.assertEqual(comisiones.first().monto_base, Decimal('80.00'))
        self.assertEqual(comisiones.first().estado, EstadoComision.PENDIENTE)