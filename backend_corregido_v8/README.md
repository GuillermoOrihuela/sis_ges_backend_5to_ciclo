# Backend — Sistema de Gestión para Negocio de Manicure

Scaffolding base generado según el **Contrato Técnico del Proyecto**.
No contiene lógica de negocio todavía: cada módulo (`usuarios`, `clientes`,
`citas`, etc.) se implementará en prompts separados, indicando siempre
`MÓDULO A IMPLEMENTAR` como pide la sección 39.

## Cómo arrancar

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements/local.txt

cp .env.example .env            # y completar SECRET_KEY, etc.

python manage.py migrate
python manage.py runserver
```

Por defecto `manage.py` usa `config.settings.local` (SQLite, DEBUG=True,
CORS abierto). Para producción: `DJANGO_SETTINGS_MODULE=config.settings.production`.

> ⚠️ `AUTH_USER_MODEL = "usuarios.Usuario"` ya está configurado en
> `config/settings/base.py`, pero el modelo `Usuario` aún no existe (se
> crea al implementar el módulo `usuarios`). Hasta entonces,
> `makemigrations`/`migrate` funcionan para el resto del proyecto, pero la
> app `usuarios` no tendrá tablas de autenticación reales.

## Qué incluye este scaffolding

- **`config/`**: settings divididos en `base.py` / `local.py` / `production.py`,
  `urls.py` + `api_router.py` (rutas oficiales de la sección 33, comentadas
  hasta que cada módulo implemente su `api/urls.py`), `wsgi.py`, `asgi.py`.
- **`common/`**: infraestructura compartida por todos los módulos:
  - `api/responses.py` + `api/mixins.py`: formato oficial de respuestas
    (sección 34) — `success_response()`, `error_response()`, y
    `ApiResponseMixin` para aplicarlo automáticamente en ViewSets.
  - `pagination/pagination.py`: `StandardResultsPagination`, ya conectada
    como `DEFAULT_PAGINATION_CLASS` en DRF, con el formato paginado oficial.
  - `exceptions/handlers.py`: `custom_exception_handler`, ya conectado como
    `EXCEPTION_HANDLER` en DRF, para que **todos** los errores (400, 401,
    403, 404, throttling) salgan en el formato oficial de error.
  - `permissions/base.py`: `role_permission(*roles)` para construir
    permisos por rol (`ADMINISTRADOR`, `GERENTE`, `RECEPCIONISTA`,
    `ESPECIALISTA`, `VENDEDOR`) sin duplicar lógica en cada módulo.
  - `models/base.py`: `TimeStampedModel`, `ActivableModel`, `BaseModel`
    (created_at/updated_at/activo) para heredar en los modelos de cada app.
  - `utils/phone.py`: `normalizar_telefono()`, usada por `clientes` y
    `citas` para la regla de "una cita activa por día" (sección 9).
- **`apps/`**: las 12 apps de dominio oficiales (sección 4), cada una con
  la estructura interna oficial exacta (sección 3): `models/`, `api/`
  (`serializers/`, `views/`, `filters/`, `urls.py`), `services/`,
  `selectors/`, `permissions/`, `validators/`, `tests/`, `migrations/`.
  Todas vacías (solo `__init__.py` y un `api/urls.py` con `urlpatterns = []`),
  listas para recibir su implementación módulo por módulo.
- **`requirements/`**: `base.txt`, `local.txt`, `production.txt`, cada
  dependencia justificada según exige la sección 1.

## COMPATIBILIDAD

```
Módulo: scaffolding base (config + common + apps vacías)
Modelos utilizados: ninguno (aún no se crea ningún modelo de negocio)
Servicios utilizados: ninguno
Endpoints utilizados: auth/login, auth/token/refresh (infraestructura JWT)
Enums utilizados: ninguno
Eventos de inventario utilizados: ninguno
No se modificó: estructura de carpetas ni nombres definidos en el contrato
```

## Siguiente paso sugerido

Implementar el módulo **`usuarios`** primero (crea `Usuario`, roles y JWT),
ya que `AUTH_USER_MODEL` depende de él y varios otros módulos
(`personal`, `pagos`, `ventas`) referencian usuarios/empleados.
