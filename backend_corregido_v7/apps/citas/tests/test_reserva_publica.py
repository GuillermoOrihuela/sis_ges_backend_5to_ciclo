from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.servicios.models import Servicio
from apps.personal.models import Empleado
from apps.citas.models import Cita, EstadoCita
from apps.clientes.models import Cliente
from datetime import date
from apps.servicios.models.servicio import CategoriaServicio
class ReservaPublicaTestCase(APITestCase):
    def setUp(self):
        self.categoria = CategoriaServicio.objects.create(nombre="General")
        # Configurar datos iniciales para la prueba
        self.empleado = Empleado.objects.create(
            nombres="Carla",
            apellidos="Pérez",
            telefono="987654321",
            cargo="ESPECIALISTA",
            fecha_ingreso=date.today(),
        )
        self.servicio = Servicio.objects.create(
            nombre="Manicure Gel",
            duracion_minutos=45,
            precio=50.00,
            categoria=self.categoria,
            activo=True
        )
        self.url = '/api/v1/public/citas/reservar/'

    def test_crear_reserva_publica_exitosa(self):
        data = {
            "nombres": "María",
            "apellidos": "Gómez",
            "telefono": "911222333",
            "email": "maria@email.com",
            "fecha": "2026-09-01",
            "hora_inicio": "10:00",
            "especialista_id": self.empleado.id,
            "servicios": [self.servicio.id]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn("codigo_reserva", response.data['data'])

    def test_restriccion_una_cita_activa_por_dia(self):
        # Crear la primera cita activa
        cliente = Cliente.objects.create(
            nombres="Lucía",
            apellidos="Torres",
            telefono="922333444"
        )
        Cita.objects.create(
            cliente=cliente,
            especialista=self.empleado,
            fecha="2026-09-02",
            hora_inicio="11:00",
            hora_fin="11:45",
            estado=EstadoCita.PENDIENTE
        )

        # Intentar reservar otra cita el mismo día con el mismo teléfono
        data = {
            "nombres": "Lucía",
            "apellidos": "Torres",
            "telefono": "922333444",
            "fecha": "2026-09-02",
            "hora_inicio": "14:00",
            "especialista_id": self.empleado.id,
            "servicios": [self.servicio.id]
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])