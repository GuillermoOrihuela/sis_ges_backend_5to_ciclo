from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..serializers.auth_serializer import CustomTokenObtainPairSerializer
from common.api.mixins import ApiResponseMixin

class LoginView(ApiResponseMixin, TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    success_message = "Inicio de sesión exitoso"

class RefreshTokenView(ApiResponseMixin, TokenRefreshView):
    success_message = "Token renovado correctamente"