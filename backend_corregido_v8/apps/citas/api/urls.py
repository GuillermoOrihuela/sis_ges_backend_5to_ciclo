from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.cita_view import ReservaPublicaAPIView, DisponibilidadPublicaAPIView, CitaGestionViewSet

router = DefaultRouter()
router.register(r'gestion/citas', CitaGestionViewSet, basename='gestion-citas')

urlpatterns = [
    # Endpoints públicos oficiales de Citas
    path('public/citas/reservar/', ReservaPublicaAPIView.as_view(), name='public-citas-reservar'),
    path('public/disponibilidad/', DisponibilidadPublicaAPIView.as_view(), name='public-disponibilidad'),
    
    # Rutas personalizadas de transiciones de estado para gestión de citas (Contrato 33)
    path('gestion/citas/<int:pk>/confirmar/', CitaGestionViewSet.as_view({'post': 'confirmar'}), name='gestion-citas-confirmar'),
    path('gestion/citas/<int:pk>/cancelar/', CitaGestionViewSet.as_view({'post': 'cancelar'}), name='gestion-citas-cancelar'),
    path('gestion/citas/<int:pk>/iniciar/', CitaGestionViewSet.as_view({'post': 'iniciar'}), name='gestion-citas-iniciar'),
    path('gestion/citas/<int:pk>/finalizar/', CitaGestionViewSet.as_view({'post': 'finalizar'}), name='gestion-citas-finalizar'),
    path('gestion/citas/<int:pk>/no-asistio/', CitaGestionViewSet.as_view({'post': 'no_asistio'}), name='gestion-citas-no-asistio'),
    path('gestion/citas/<int:pk>/reprogramar/', CitaGestionViewSet.as_view({'post': 'reprogramar'}), name='gestion-citas-reprogramar'),

    path('', include(router.urls)),
]