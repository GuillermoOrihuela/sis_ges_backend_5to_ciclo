from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Documentación OpenAPI / Swagger
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Rutas de los módulos implementados
    path('api/v1/', include('apps.usuarios.api.urls')),
    path('api/v1/', include('apps.clientes.api.urls')),
    path('api/v1/', include('apps.servicios.api.urls')),
    path('api/v1/', include('apps.personal.api.urls')),
    path('api/v1/', include('apps.citas.api.urls')),
    path('api/v1/', include('apps.inventario.api.urls')),
    path('api/v1/', include('apps.ventas.api.urls')),
    path('api/v1/', include('apps.pagos.api.urls')),
    path('api/v1/', include('apps.comisiones.api.urls')),
]