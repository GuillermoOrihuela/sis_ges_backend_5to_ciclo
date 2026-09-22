from .base import *

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/julio32/sis_ges_backend_5to_ciclo/db.sqlite3',
    }
}