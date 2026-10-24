from rest_framework.response import Response
from rest_framework import status


def is_mobile_client(request):
    """
    Detect whether the incoming HTTP request is originated from the Flutter mobile app.
    Dart's http client automatically sets User-Agent containing 'Dart/<version>'
    or the mobile app can pass an explicit 'X-Client: mobile' header.
    """
    if not request:
        return False
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    x_client = request.META.get('HTTP_X_CLIENT', '').lower()
    if 'dart' in user_agent or x_client in ('mobile', 'flutter'):
        return True
    return False


def api_response(data=None, message="Success", status_code=status.HTTP_200_OK, request=None, force_envelope=False):
    """
    Dual-compatibility response dispatcher:
    - When Flutter calls the endpoint: returns {"success": True, "message": message, "data": ...}
      which matches Flutter's `data['data']` checks.
    - When React Admin calls the endpoint: returns `data` directly (e.g. array or object)
      which strictly satisfies Next.js / TanStack Query Zod schema validation.
    """
    if force_envelope or (request and is_mobile_client(request)):
        payload = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }
        return Response(payload, status=status_code)

    return Response(data if data is not None else {}, status=status_code)


def error_response(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, request=None):
    """
    Compatible error response providing both 'message' and 'detail' keys
    so both Flutter UI banners and DRF/React error handlers capture the failure cleanly.
    """
    payload = {
        "success": False,
        "message": message,
        "detail": message,
        "errors": errors if errors is not None else {}
    }
    return Response(payload, status=status_code)
