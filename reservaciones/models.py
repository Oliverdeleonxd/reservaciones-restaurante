from django.db import models  # type: ignore[import-untyped]

import uuid


class ConfiguracionRestaurante(models.Model):
    hora_apertura = models.TimeField()
    hora_cierre = models.TimeField()
    intervalo_minutos = models.IntegerField(default=60)
    duracion_reserva_minutos = models.IntegerField(default=90)

    class Meta:
        verbose_name = "Configuración del Restaurante"

    def __str__(self):
        return f"Configuración: {self.hora_apertura} - {self.hora_cierre}"


class Mesa(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    capacidad = models.IntegerField()
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Mesa"
        verbose_name_plural = "Mesas"

    def __str__(self):
        return f"Mesa {self.numero} (capacidad: {self.capacidad})"


class Reservacion(models.Model):
    STATUS_CHOICES = [
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha = models.DateField()
    hora = models.TimeField()
    personas = models.IntegerField()
    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT)
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmada')
    codigo_cancelacion = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reservación"
        verbose_name_plural = "Reservaciones"

    def __str__(self):
        return f"{self.nombre} - Mesa {self.mesa.numero} - {self.fecha} {self.hora}"
