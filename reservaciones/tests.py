from django.test import TestCase # type: ignore[import-untyped]
from django.contrib.auth.models import User # type: ignore[import-untyped]
from rest_framework.test import APIClient # type: ignore[import-untyped]
from rest_framework import status # type: ignore[import-untyped]
from datetime import date, time # type: ignore[import-untyped]
from .models import Mesa, Reservacion, ConfiguracionRestaurante # type: ignore[import-untyped]


class BaseTestCase(TestCase):
    def setUp(self):
        # Configuración del restaurante
        self.config = ConfiguracionRestaurante.objects.create(
            hora_apertura=time(12, 0),
            hora_cierre=time(22, 0),
            intervalo_minutos=60,
            duracion_reserva_minutos=90
        )

        # Mesas de prueba
        self.mesa1 = Mesa.objects.create(numero='T1', capacidad=2, activa=True)
        self.mesa2 = Mesa.objects.create(numero='T2', capacidad=4, activa=True)

        # Cliente API
        self.client = APIClient()

        # Usuario admin
        self.admin = User.objects.create_superuser(
            username='testadmin',
            password='testpass123'
        )

        # Fecha futura para pruebas
        self.fecha_futura = date(2027, 6, 15)


class TestCrearReservacion(BaseTestCase):

    def test_reservacion_valida(self):
        """Debe crear una reservación exitosamente"""
        response = self.client.post('/api/reservations/', {
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com',
            'telefono': '6000-0000',
            'fecha': str(self.fecha_futura),
            'hora': '14:00:00',
            'personas': 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('codigo_cancelacion', response.data)
        self.assertIn('mesa', response.data)

    def test_reservacion_en_pasado(self):
        """No debe permitir reservar en el pasado"""
        response = self.client.post('/api/reservations/', {
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com',
            'telefono': '6000-0000',
            'fecha': '2020-01-01',
            'hora': '14:00:00',
            'personas': 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_horario_invalido(self):
        """No debe permitir reservar fuera del horario"""
        response = self.client.post('/api/reservations/', {
            'nombre': 'Juan Pérez',
            'email': 'juan@test.com',
            'telefono': '6000-0000',
            'fecha': str(self.fecha_futura),
            'hora': '08:00:00',
            'personas': 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestDisponibilidad(BaseTestCase):

    def test_sin_mesas_disponibles(self):
        """Debe fallar cuando todas las mesas están ocupadas"""
        # Ocupar todas las mesas con capacidad suficiente
        Reservacion.objects.create(
            nombre='Cliente 1', email='c1@test.com', telefono='111',
            fecha=self.fecha_futura, hora=time(14, 0),
            personas=2, mesa=self.mesa1, estado='confirmada'
        )
        Reservacion.objects.create(
            nombre='Cliente 2', email='c2@test.com', telefono='222',
            fecha=self.fecha_futura, hora=time(14, 0),
            personas=2, mesa=self.mesa2, estado='confirmada'
        )

        response = self.client.post('/api/reservations/', {
            'nombre': 'Cliente 3',
            'email': 'c3@test.com',
            'telefono': '333',
            'fecha': str(self.fecha_futura),
            'hora': '14:00:00',
            'personas': 2
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_capacidad_insuficiente(self):
        """Debe fallar cuando no hay mesa con capacidad suficiente"""
        response = self.client.post('/api/reservations/', {
            'nombre': 'Grupo Grande',
            'email': 'grupo@test.com',
            'telefono': '6000-0000',
            'fecha': str(self.fecha_futura),
            'hora': '14:00:00',
            'personas': 10
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestCancelarReservacion(BaseTestCase):

    def test_cancelar_con_codigo(self):
        """Cliente puede cancelar con su código único"""
        reservacion = Reservacion.objects.create(
            nombre='Juan', email='juan@test.com', telefono='111',
            fecha=self.fecha_futura, hora=time(14, 0),
            personas=2, mesa=self.mesa1, estado='confirmada'
        )

        response = self.client.post(
            f'/api/reservations/cancel/{reservacion.codigo_cancelacion}/'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reservacion.refresh_from_db()
        self.assertEqual(reservacion.estado, 'cancelada')