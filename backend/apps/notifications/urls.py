from django.urls import path
from .views import NotificationListView, NotificationDeleteView, NotificationClearAllView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('<uuid:notification_id>/', NotificationDeleteView.as_view(), name='notification_delete'),
    path('clear-all/', NotificationClearAllView.as_view(), name='notification_clear_all'),
]
