from django.urls import path, include # type: ignore[import-untyped]
from rest_framework.routers import DefaultRouter
from . import views # type: ignore[import-untyped]

router = DefaultRouter()
router.register(r'mesas', views.MesaViewSet)
router.register(r'reservaciones', views.ReservacionViewSet)
router.register(r'configuracion', views.ConfiguracionViewSet)

urlpatterns = [
    # Públicas
    path('availability/', views.disponibilidad, name='disponibilidad'),
    path('reservations/', views.crear_reserva, name='crear-reserva'),
    path('reservations/cancel/<uuid:codigo>/', views.cancelar_reserva, name='cancelar-reserva'),

    # Admin
    path('admin-panel/reservations/<int:pk>/cancel/', views.cancelar_reserva_admin, name='cancelar-admin'),
    path('admin-panel/metrics/', views.metricas_ocupacion, name='metricas'),

    path('', include(router.urls)),
]