"""
Router central de la API v1.

Agrupa los endpoints oficiales definidos en la sección 33 del Contrato
Técnico. Las rutas de autenticación son infraestructura genérica (SimpleJWT)
y ya están activas. Las rutas de cada módulo de negocio se descomentan
cuando ese módulo implementa su api/urls.py real (ver secciones 39-40).
"""
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ── Autenticación (sección 33) ──────────────────────────────────────
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ── Públicos ─────────────────────────────────────────────────────────
    # path("public/servicios/", include("apps.servicios.api.urls")),
    # path("public/especialistas/", include("apps.personal.api.urls")),
    # path("public/disponibilidad/", include("apps.citas.api.urls")),
    # path("public/citas/", include("apps.citas.api.urls")),

    # ── Gestión de citas ────────────────────────────────────────────────
    # path("gestion/citas/", include("apps.citas.api.urls")),

    # ── Gestión de ventas ───────────────────────────────────────────────
    # path("gestion/ventas/", include("apps.ventas.api.urls")),

    # ── Gestión de pagos ────────────────────────────────────────────────
    # path("gestion/pagos/", include("apps.pagos.api.urls")),

    # ── Gestión de personal ─────────────────────────────────────────────
    # path("gestion/empleados/", include("apps.personal.api.urls")),
    # path("gestion/turnos/", include("apps.personal.api.urls")),
    # path("gestion/horarios/", include("apps.personal.api.urls")),
    # path("gestion/ausencias/", include("apps.personal.api.urls")),

    # ── Gestión de inventario ───────────────────────────────────────────
    # path("gestion/productos/", include("apps.inventario.api.urls")),
    # path("gestion/almacenes/", include("apps.inventario.api.urls")),
    # path("gestion/existencias/", include("apps.inventario.api.urls")),
    # path("gestion/movimientos-inventario/", include("apps.inventario.api.urls")),
    # path("gestion/kardex/", include("apps.inventario.api.urls")),

    # ── Gestión de comisiones ───────────────────────────────────────────
    # path("gestion/comisiones/", include("apps.comisiones.api.urls")),
]
