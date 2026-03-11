from rest_framework import serializers # type: ignore[import-untyped]
from django.utils import timezone
from .models import Mesa, Reservacion, ConfiguracionRestaurante  # type: ignore[import-untyped]


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = '__all__'


class ConfiguracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionRestaurante
        fields = '__all__'


class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = '__all__'
        read_only_fields = ['mesa', 'estado', 'codigo_cancelacion', 'creada_en']


class CrearReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = ['nombre', 'email', 'telefono', 'fecha', 'hora', 'personas']

    def validate_fecha(self, value):
        hoy = timezone.now().date()
        if value < hoy:
            raise serializers.ValidationError("No puedes reservar en una fecha pasada.")
        return value

    def validate_personas(self, value):
        if value <= 0:
            raise serializers.ValidationError("El número de personas debe ser mayor a 0.")
        return value

    def validate(self, data):
        from .services import validar_disponibilidad # type: ignore[import-untyped]
        fecha = data.get('fecha')
        hora = data.get('hora')
        personas = data.get('personas')

        validar_disponibilidad(fecha, hora, personas)
        return data