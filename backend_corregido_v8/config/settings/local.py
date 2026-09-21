from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# En local, además del dominio de producción (heredado de base.py), se
# permiten los orígenes típicos del servidor de desarrollo de Vite para no
# tener que desactivar CORS mientras se prueba en la máquina del
# desarrollador.
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS + [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]