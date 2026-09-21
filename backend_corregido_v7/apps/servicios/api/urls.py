from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.servicio_view import ServicioPublicoViewSet, ServicioGestionViewSet, CategoriaServicioViewSet

router = DefaultRouter()
router.register(r'gestion/servicios', ServicioGestionViewSet, basename='gestion-servicios')
router.register(r'gestion/categorias-servicio', CategoriaServicioViewSet, basename='gestion-categorias-servicio')

urlpatterns = [
    # Endpoint público oficial
    path('public/servicios/', ServicioPublicoViewSet.as_view({'get': 'list'}), name='public-servicios'),
    path('', include(router.urls)),
]