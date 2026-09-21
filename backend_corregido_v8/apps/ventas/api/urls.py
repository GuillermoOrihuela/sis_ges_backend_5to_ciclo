from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.venta_view import VentaViewSet

app_name = "ventas"

router = DefaultRouter()
router.register(r'gestion/ventas', VentaViewSet, basename='gestion-ventas')

urlpatterns = [
    path('gestion/ventas/<int:pk>/confirmar/', VentaViewSet.as_view({'post': 'confirmar'}), name='gestion-ventas-confirmar'),
    path('gestion/ventas/<int:pk>/anular/', VentaViewSet.as_view({'post': 'anular'}), name='gestion-ventas-anular'),
    path('', include(router.urls)),
]
