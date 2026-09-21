from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.cliente_view import ClienteViewSet

router = DefaultRouter()
router.register(r'gestion/clientes', ClienteViewSet, basename='gestion-clientes')

urlpatterns = [
    path('', include(router.urls)),
]