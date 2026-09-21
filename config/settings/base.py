import os
from pathlib import Path
import environ

# Directorio raíz del proyecto (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)

# Leer archivo .env si existe
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-key-for-dev')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Aplicaciones instaladas según Contrato Técnico
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de terceros obligatorias
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',

    # Módulos del Sistema (Aplicaciones del proyecto)
    'apps.usuarios',
    'apps.clientes',
    'apps.servicios',
    'apps.citas',
    'apps.personal',
    'apps.ventas',
    'apps.pagos',
    'apps.comisiones',
    'apps.inventario',
    'apps.informes',
    'apps.auditoria',
    'apps.configuracion',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///db.sqlite3')
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
];

LANGUAGE_CODE = 'es-PE'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración global de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'common.api.pagination.StandardPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'common.exceptions.handlers.custom_exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # Throttling básico (hallazgo #9 de INTEGRACION_BACKEND.md): sin esto,
    # /auth/login/ y los endpoints públicos quedaban sin límite de peticiones.
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '120/minute',
    },
}

# Configuración de SimpleJWT (hallazgo #4 de INTEGRACION_BACKEND.md).
# NOTA: para que BLACKLIST_AFTER_ROTATION tenga efecto real (invalidar
# refresh tokens robados o tras logout) todavía falta:
#   1) agregar 'rest_framework_simplejwt.token_blacklist' a INSTALLED_APPS,
#   2) correr sus migraciones,
#   3) exponer un endpoint de logout que llame a RefreshToken(token).blacklist().
# Sin esos 3 pasos, ROTATE_REFRESH_TOKENS ya ayuda (un refresh usado una vez
# deja de servir), pero un token nunca usado sigue siendo válido 1 día.
from datetime import timedelta  # noqa: E402

SIMPLE_JWT = {
    # Sesión de 8 horas: el access token dura 30 min y el refresh 8 horas.
    # OJO: con ROTATE_REFRESH_TOKENS, cada refresh emite un token nuevo con
    # su propio reloj de 8h, así que esto es un "tiempo de inactividad
    # máximo de 8h", no un tope absoluto desde el login (si el usuario sigue
    # activo, la sesión se sigue renovando). Si se necesita un tope
    # absoluto real, hay que guardar la fecha de login original como claim
    # personalizado y validarla en un serializer de refresh a medida.
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=8),
    'ROTATE_REFRESH_TOKENS': True,
}

# Configuración de DRF Spectacular (Swagger)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Sistema Profesional de Gestión - Manicure API',
    'DESCRIPTION': 'API oficial para la gestión de salón de manicure',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = [
#     'https://sis-ges-frotend-5to-ciclo.vercel.app',
# ]
# Necesario para que el navegador mande la cookie/credenciales (o el header
# Authorization con el JWT) en las peticiones cross-origin desde ese dominio.
CORS_ALLOW_CREDENTIALS = True


AUTH_USER_MODEL = 'usuarios.Usuario'