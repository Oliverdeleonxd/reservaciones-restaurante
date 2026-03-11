from rest_framework import status, viewsets # type: ignore[import-untyped]
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny # type: ignore[import-untyped]
from rest_framework.response import Response
from django.utils import timezone # type: ignore[import-untyped]
from .models import Mesa, Reservacion, ConfiguracionRestaurante # type: ignore[import-untyped]
from .serializers import (
    MesaSerializer,
    ReservacionSerializer,
    CrearReservacionSerializer,
    ConfiguracionSerializer
)
from .services import crear_reservacion # type: ignore[import-untyped]


# ─── PÚBLICAS ───────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def disponibilidad(request):
    fecha_str = request.query_params.get('date')
    hora_str = request.query_params.get('time')
    personas = request.query_params.get('personas', 2)

    if not fecha_str:
        return Response({'error': 'El parámetro date es requerido.'}, status=400)

    try:
        from datetime import date, time
        fecha = date.fromisoformat(fecha_str)
        personas = int(personas)
    except ValueError:
        return Response({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD.'}, status=400)

    from .services import get_configuracion # type: ignore[import-untyped]
    config = get_configuracion()

    # Generar horarios disponibles
    from datetime import datetime, timedelta
    horarios_disponibles = []
    hora_actual = datetime.combine(fecha, config.hora_apertura)
    hora_cierre = datetime.combine(fecha, config.hora_cierre)

    while hora_actual < hora_cierre:
        hora = hora_actual.time()
        try:
            from .services import validar_disponibilidad # type: ignore[import-untyped]
            validar_disponibilidad(fecha, hora, personas)
            horarios_disponibles.append(hora.strftime('%H:%M'))
        except Exception:
            pass
        hora_actual += timedelta(minutes=config.intervalo_minutos)

    return Response({
        'fecha': fecha_str,
        'personas': personas,
        'horarios_disponibles': horarios_disponibles
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def crear_reserva(request):
    serializer = CrearReservacionSerializer(data=request.data)
    if serializer.is_valid():
        try:
            reservacion = crear_reservacion(serializer.validated_data)
            return Response({
                'mensaje': 'Mesa reservada exitosamente.',
                'codigo_cancelacion': str(reservacion.codigo_cancelacion),
                'mesa': reservacion.mesa.numero,
                'fecha': reservacion.fecha,
                'hora': reservacion.hora,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def cancelar_reserva(request, codigo):
    try:
        reservacion = Reservacion.objects.get(
            codigo_cancelacion=codigo,
            estado='confirmada'
        )
        if reservacion.fecha < timezone.now().date():
            return Response({'error': 'No puedes cancelar una reserva pasada.'}, status=400)

        reservacion.estado = 'cancelada'
        reservacion.save()
        return Response({'mensaje': 'Reservación cancelada exitosamente.'})
    except Reservacion.DoesNotExist:
        return Response({'error': 'Código de cancelación inválido.'}, status=404)


# ─── ADMIN ──────────────────────────────────────────────

class MesaViewSet(viewsets.ModelViewSet):
    queryset = Mesa.objects.all()
    serializer_class = MesaSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        mesa = self.get_object()
        hoy = timezone.now().date()
        tiene_reservas_futuras = Reservacion.objects.filter(
            mesa=mesa,
            fecha__gte=hoy,
            estado='confirmada'
        ).exists()

        if tiene_reservas_futuras:
            return Response(
                {'error': 'No puedes eliminar una mesa con reservas futuras.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ReservacionViewSet(viewsets.ModelViewSet):
    queryset = Reservacion.objects.all().order_by('-fecha', '-hora')
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        estado = self.request.query_params.get('estado')

        if fecha:
            queryset = queryset.filter(fecha=fecha)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancelar_reserva_admin(request, pk):
    try:
        reservacion = Reservacion.objects.get(pk=pk)
        reservacion.estado = 'cancelada'
        reservacion.save()
        return Response({'mensaje': 'Reservación cancelada por el administrador.'})
    except Reservacion.DoesNotExist:
        return Response({'error': 'Reservación no encontrada.'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def metricas_ocupacion(request):
    fecha_str = request.query_params.get('fecha')
    if not fecha_str:
        from datetime import date
        fecha = date.today()
    else:
        from datetime import date
        fecha = date.fromisoformat(fecha_str)

    total_mesas = Mesa.objects.filter(activa=True).count()
    reservas_del_dia = Reservacion.objects.filter(
        fecha=fecha,
        estado='confirmada'
    ).count()

    ocupacion = (reservas_del_dia / total_mesas * 100) if total_mesas > 0 else 0

    return Response({
        'fecha': str(fecha),
        'total_mesas': total_mesas,
        'reservas_confirmadas': reservas_del_dia,
        'ocupacion_porcentaje': round(ocupacion, 2)
    })


class ConfiguracionViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionRestaurante.objects.all()
    serializer_class = ConfiguracionSerializer
    permission_classes = [IsAuthenticated]