from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom_data = {
            "success": False,
            "message": "Error en la solicitud",
            "errors": response.data
        }
        response.data = custom_data

    return response