from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.comision_view import ComisionViewSet

app_name = "comisiones"

router = DefaultRouter()
router.register(r'gestion/comisiones', ComisionViewSet, basename='gestion-comisiones')

urlpatterns = [
    path('gestion/comisiones/<int:pk>/aprobar/', ComisionViewSet.as_view({'post': 'aprobar'}), name='gestion-comisiones-aprobar'),
    path('gestion/comisiones/<int:pk>/pagar/', ComisionViewSet.as_view({'post': 'pagar'}), name='gestion-comisiones-pagar'),
    path('gestion/comisiones/<int:pk>/anular/', ComisionViewSet.as_view({'post': 'anular'}), name='gestion-comisiones-anular'),
    path('', include(router.urls)),
]
