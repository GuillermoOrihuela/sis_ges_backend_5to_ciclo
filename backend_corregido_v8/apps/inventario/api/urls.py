from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.inventario_view import (
    CategoriaProductoViewSet, AlmacenViewSet, ProductoViewSet,
    ExistenciaViewSet, MovimientoInventarioViewSet,
)

app_name = "inventario"

router = DefaultRouter()
router.register(r'gestion/categorias-producto', CategoriaProductoViewSet, basename='gestion-categorias-producto')
router.register(r'gestion/almacenes', AlmacenViewSet, basename='gestion-almacenes')
router.register(r'gestion/productos', ProductoViewSet, basename='gestion-productos')
router.register(r'gestion/existencias', ExistenciaViewSet, basename='gestion-existencias')
router.register(r'gestion/movimientos-inventario', MovimientoInventarioViewSet, basename='gestion-movimientos-inventario')

urlpatterns = [
    path('', include(router.urls)),
]
