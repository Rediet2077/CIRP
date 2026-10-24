from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Standardize exception responses across both frontend applications.
    """
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred."
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                message = str(response.data['detail'])
            elif response.data:
                first_key = next(iter(response.data))
                first_val = response.data[first_key]
                message = f"{first_key}: {first_val}" if isinstance(first_val, str) else f"{first_key}: {first_val[0]}"
        elif isinstance(response.data, list) and response.data:
            message = str(response.data[0])

        response.data = {
            'success': False,
            'message': message,
            'detail': message,
            'errors': response.data
        }

    return response
