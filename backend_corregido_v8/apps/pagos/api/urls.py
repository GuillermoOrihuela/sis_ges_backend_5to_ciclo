from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.pago_view import PagoViewSet, CajaResumenAPIView

app_name = "pagos"

router = DefaultRouter()
router.register(r'gestion/pagos', PagoViewSet, basename='gestion-pagos')

urlpatterns = [
    path('gestion/pagos/<int:pk>/anular/', PagoViewSet.as_view({'post': 'anular'}), name='gestion-pagos-anular'),
    path('gestion/caja/resumen/', CajaResumenAPIView.as_view(), name='gestion-caja-resumen'),
    path('', include(router.urls)),
]
