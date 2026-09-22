from .base import *

DEBUG = False

# Configuración explícita de SQLite para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path('/home/julio32/sis_ges_backend_5to_ciclo/db.sqlite3'),
    }
}