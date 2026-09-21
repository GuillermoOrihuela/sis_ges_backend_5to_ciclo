"""
Normalización de números telefónicos.

El contrato exige (sección 6 y sección 9) identificar a un cliente por su
teléfono normalizado, para poder validar que no tenga más de una cita
activa el mismo día. Esta función centraliza esa normalización para que
todos los módulos (clientes, citas) usen el mismo criterio.
"""
import re

PREFIJO_PERU = "51"


def normalizar_telefono(telefono: str) -> str:
    """
    Deja solo dígitos y, si el número viene con el prefijo de país de Perú
    (+51 / 0051) seguido de un número local de 9 dígitos, remueve el
    prefijo para quedarse con el número local.

    Ejemplos:
        "+51 999 999 999" -> "999999999"
        "51999999999"      -> "999999999"
        "999-999-999"      -> "999999999"
    """
    if not telefono:
        return ""

    digitos = re.sub(r"\D", "", telefono)

    if digitos.startswith(PREFIJO_PERU) and len(digitos) == len(PREFIJO_PERU) + 9:
        digitos = digitos[len(PREFIJO_PERU):]

    return digitos
