"""Master URL configuration for CIRP platform."""
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.reports.views import PublicReportListView


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """CIRP Platform API Health & Status check."""
    return Response({
        'name': 'Community Infrastructure Reporting Platform (CIRP) API',
        'version': '1.0.0',
        'status': 'online',
        'endpoints': {
            'auth': '/api/v1/auth/',
            'users': '/api/v1/users/',
            'departments': '/api/v1/departments/',
            'categories': '/api/v1/categories/',
            'assets': '/api/v1/assets/',
            'asset_types': '/api/v1/asset-types/',
            'reports': '/api/v1/reports/',
            'my_reports': '/api/v1/reports/my-reports/',
            'contractors': '/api/v1/contractors/',
            'tasks': '/api/v1/tasks/',
            'extensions': '/api/v1/extensions/',
            'public_reports': '/api/v1/public/reports/',
        }
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root, name='api_root'),
    path('api/v1/', api_root, name='api_v1_root'),

    # Public transparency routes
    path('api/v1/public/reports/', PublicReportListView.as_view(), name='api_v1_public_reports'),
    path('api/v1/public/reports', PublicReportListView.as_view(), name='api_v1_public_reports_no_slash'),
    path('public/reports/', PublicReportListView.as_view(), name='public_reports'),
    path('public/reports', PublicReportListView.as_view(), name='public_reports_no_slash'),

    # Versioned API routes (/api/v1/...)
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/departments/', include('apps.departments.urls')),
    path('api/v1/categories/', include('apps.categories.urls')),
    path('api/v1/', include('apps.assets.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/contractors/', include('apps.contractors.urls')),
    path('api/v1/tasks/', include('apps.tasks.urls')),
    path('api/v1/extensions/', include('apps.extensions.urls')),

    # Direct routes supporting React Admin Better Fetch client
    path('', include('apps.users.urls')),
    path('departments/', include('apps.departments.urls')),
    path('categories/', include('apps.categories.urls')),
    path('', include('apps.assets.urls')),
    path('reports/', include('apps.reports.urls')),
    path('contractors/', include('apps.contractors.urls')),
    path('tasks/', include('apps.tasks.urls')),
    path('extensions/', include('apps.extensions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
