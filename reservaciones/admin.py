from django.contrib import admin # type: ignore[import-untyped]

from .models import Mesa, Reservacion, ConfiguracionRestaurante  # type: ignore[import-untyped]


@admin.register(ConfiguracionRestaurante)
class ConfiguracionAdmin(admin.ModelAdmin):
    list_display = ['hora_apertura', 'hora_cierre', 'intervalo_minutos', 'duracion_reserva_minutos']


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ['numero', 'capacidad', 'activa']
    list_filter = ['activa']


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'mesa', 'fecha', 'hora', 'personas', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['nombre', 'email']
