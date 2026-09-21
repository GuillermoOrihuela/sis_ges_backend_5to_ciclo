from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.empleado_view import (
    EmpleadoViewSet, EspecialistaPublicoViewSet, TurnoViewSet, 
    HorarioEmpleadoViewSet, AusenciaEmpleadoViewSet
)

router = DefaultRouter()
router.register(r'gestion/empleados', EmpleadoViewSet, basename='gestion-empleados')
router.register(r'gestion/turnos', TurnoViewSet, basename='gestion-turnos')
router.register(r'gestion/horarios', HorarioEmpleadoViewSet, basename='gestion-horarios')
router.register(r'gestion/ausencias', AusenciaEmpleadoViewSet, basename='gestion-ausencias')

urlpatterns = [
    # Endpoint público oficial de especialistas
    path('public/especialistas/', EspecialistaPublicoViewSet.as_view({'get': 'list'}), name='public-especialistas'),
    path('', include(router.urls)),
]