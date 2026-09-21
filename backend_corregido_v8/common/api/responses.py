from rest_framework.response import Response
from rest_framework import status


def success_response(data=None, message="Éxito", status_code=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status_code)

def error_response(message="Error", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status_code)

class APIResponse:
    @staticmethod
    def success(data=None, message="Operación realizada correctamente", status_code=status.HTTP_200_OK):
        response_data = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }
        return Response(response_data, status=status.HTTP_200_OK if status_code == 200 else status_code)

    @staticmethod
    def error(message="Error de validación", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        response_data = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {}
        }
        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(data, pagination_info, message="Consulta realizada correctamente"):
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "pagination": pagination_info
        }
        return Response(response_data, status=status.HTTP_200_OK)