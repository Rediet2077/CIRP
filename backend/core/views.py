from django.http import JsonResponse
from django.conf import settings


def api_root(request):
    """
    Root endpoint that provides API information and available endpoints.
    """
    return JsonResponse({
        "service": "CIRP Backend API",
        "version": "1.0.0",
        "status": "running",
        "debug": settings.DEBUG,
        "documentation": {
            "admin_panel": "/admin/",
            "api_reference": "See API_REFERENCE.md in project root"
        },
        "endpoints": {
            "authentication": {
                "register": "/api/v1/auth/register/",
                "login": "/api/v1/auth/login/",
                "token_refresh": "/api/v1/auth/token/refresh/",
                "change_password": "/api/v1/auth/change-password/"
            },
            "users": {
                "profile": "/api/v1/users/me/",
                "list": "/api/v1/users/",
                "detail": "/api/v1/users/<uuid>/"
            },
            "reports": {
                "submit_public": "/submit-report/",
                "list": "/api/v1/reports/",
                "detail": "/api/v1/reports/<uuid>/"
            },
            "categories": {
                "list": "/api/v1/categories/",
                "detail": "/api/v1/categories/<uuid>/"
            },
            "departments": {
                "list": "/api/v1/departments/",
                "detail": "/api/v1/departments/<uuid>/"
            },
            "notifications": {
                "list": "/api/v1/notifications/",
                "detail": "/api/v1/notifications/<uuid>/"
            },
            "audit": {
                "logs": "/api/v1/audit-logs/",
                "detail": "/api/v1/audit-logs/<uuid>/"
            }
        },
        "ai_service": {
            "url": settings.AI_SERVICE_URL,
            "endpoints": [
                "POST /ai/classify-image/",
                "POST /ai/detect-duplicate/",
                "POST /ai/compare-multilingual/",
                "POST /ai/detect-language/",
                "POST /ai/check-quality/",
                "POST /ai/auto-fill/"
            ]
        },
        "message": "Welcome to CIRP API! All endpoints require authentication except /submit-report/ and /api/v1/auth/*"
    }, json_dumps_params={'indent': 2})
