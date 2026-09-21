from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_view import LoginView, RefreshTokenView
from .views.usuario_view import UsuarioViewSet, MeAPIView

router = DefaultRouter()
router.register(r'gestion/usuarios', UsuarioViewSet, basename='gestion-usuarios')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/token/refresh/', RefreshTokenView.as_view(), name='auth-token-refresh'),
    path('auth/me/', MeAPIView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]