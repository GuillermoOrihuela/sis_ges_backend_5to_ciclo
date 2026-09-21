from apps.configuracion.models import ConfiguracionNegocio

def obtener_configuracion_negocio():
    """
    Retorna la instancia única de configuración del negocio (Singleton pattern básico).
    """
    config, created = ConfiguracionNegocio.objects.get_or_create(id=1)
    return config