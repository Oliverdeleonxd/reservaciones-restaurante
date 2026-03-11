from datetime import datetime, timedelta
from django.db import transaction  # type: ignore[import-untyped]
from rest_framework.exceptions import ValidationError
from .models import Mesa, Reservacion, ConfiguracionRestaurante  # type: ignore[import-untyped]

 
def get_configuracion():
    config = ConfiguracionRestaurante.objects.first()
    if not config:
        raise ValidationError("El restaurante no tiene horario configurado.")
    return config


def validar_disponibilidad(fecha, hora, personas, reservacion_id=None):
    config = get_configuracion()

    # Validar horario
    if hora < config.hora_apertura or hora >= config.hora_cierre:
        raise ValidationError("La hora está fuera del horario del restaurante.")

    # Calcular rango horario de la reserva
    inicio = datetime.combine(fecha, hora)
    fin = inicio + timedelta(minutes=config.duracion_reserva_minutos)
    hora_fin = fin.time()

    # Buscar mesas con capacidad suficiente
    mesas_disponibles = Mesa.objects.filter(
        activa=True,
        capacidad__gte=personas
    )

    if not mesas_disponibles.exists():
        raise ValidationError("No hay mesas con capacidad suficiente.")

    # Verificar cuál mesa está libre en ese horario
    for mesa in mesas_disponibles:
        reservas_conflicto = Reservacion.objects.filter(
            mesa=mesa,
            fecha=fecha,
            estado='confirmada',
            hora__lt=hora_fin,
        ).exclude(id=reservacion_id)

        # Verificar solapamiento
        tiene_conflicto = False
        for reserva in reservas_conflicto:
            inicio_existente = datetime.combine(fecha, reserva.hora)
            fin_existente = inicio_existente + timedelta(minutes=config.duracion_reserva_minutos)
            inicio_nueva = datetime.combine(fecha, hora)

            if inicio_nueva < fin_existente and fin.time() > reserva.hora:
                tiene_conflicto = True
                break

        if not tiene_conflicto:
            return mesa  # Mesa disponible encontrada

    raise ValidationError("No hay disponibilidad para la fecha y hora seleccionadas.")


@transaction.atomic
def crear_reservacion(data):
    fecha = data['fecha']
    hora = data['hora']
    personas = data['personas']

    # select_for_update evita doble reserva simultánea
    Mesa.objects.select_for_update().filter(activa=True, capacidad__gte=personas)

    mesa = validar_disponibilidad(fecha, hora, personas)

    reservacion = Reservacion.objects.create(
        nombre=data['nombre'],
        email=data['email'],
        telefono=data['telefono'],
        fecha=fecha,
        hora=hora,
        personas=personas,
        mesa=mesa,
        estado='confirmada'
    )

    return reservacion