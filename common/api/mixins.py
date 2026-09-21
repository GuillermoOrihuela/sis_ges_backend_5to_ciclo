"""
Mixin opcional para que cualquier vista basada en clases (APIView,
GenericAPIView, ViewSet) devuelva automáticamente el formato oficial de
respuesta (sección 34), sin tener que envolver manualmente cada retorno.

Uso:

    class CitaViewSet(ApiResponseMixin, viewsets.ModelViewSet):
        ...

Las respuestas ya paginadas (que vienen de StandardResultsPagination) y las
respuestas de error (que vienen de custom_exception_handler) ya incluyen la
clave "success", así que este mixin no las vuelve a envolver.
"""


class ApiResponseMixin:
    #: Mensaje de éxito por defecto cuando la vista no define uno propio.
    default_success_message = "Operación realizada correctamente"

    def finalize_response(self, request, response, *args, **kwargs):
        already_wrapped = (
            hasattr(response, "data")
            and isinstance(response.data, dict)
            and "success" in response.data
        )
        has_body = hasattr(response, "data") and response.data is not None
        if not response.exception and has_body and not already_wrapped:
            response.data = {
                "success": True,
                "message": getattr(self, "success_message", self.default_success_message),
                "data": response.data,
            }
        return super().finalize_response(request, response, *args, **kwargs)
