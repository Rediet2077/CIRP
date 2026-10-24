from django.urls import path
from .views import (
    ReportListCreateView,
    CitizenMyReportsView,
    CitizenReportDeleteView,
    ReportDetailView,
    AcceptReportView,
    RejectReportView,
    LinkAssetView,
    PublicReportListView,
)

urlpatterns = [
    # Citizen personal report history
    path('my-reports/', CitizenMyReportsView.as_view(), name='citizen_my_reports'),
    path('my-reports', CitizenMyReportsView.as_view(), name='citizen_my_reports_no_slash'),

    # Public transparency reports (also exposed at top-level)
    path('public/', PublicReportListView.as_view(), name='public_reports_nested'),

    # Admin triage actions
    path('<str:pk>/accept/', AcceptReportView.as_view(), name='report_accept'),
    path('<str:pk>/accept', AcceptReportView.as_view(), name='report_accept_no_slash'),
    path('<str:pk>/reject/', RejectReportView.as_view(), name='report_reject'),
    path('<str:pk>/reject', RejectReportView.as_view(), name='report_reject_no_slash'),
    path('<str:pk>/link-asset/', LinkAssetView.as_view(), name='report_link_asset'),
    path('<str:pk>/link-asset', LinkAssetView.as_view(), name='report_link_asset_no_slash'),
    path('<str:pk>/citizen-delete/', CitizenReportDeleteView.as_view(), name='citizen_report_delete'),

    # Single report detail
    path('<str:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('<str:pk>', ReportDetailView.as_view(), name='report_detail_no_slash'),

    # List & Create reports
    path('', ReportListCreateView.as_view(), name='reports_list_create'),
]
