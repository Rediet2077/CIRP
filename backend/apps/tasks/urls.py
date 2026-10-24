from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    TaskProgressView,
    TaskCompletionView,
    TaskVerifyResolveView,
    TaskReturnRejectView,
)

urlpatterns = [
    # Task progress update
    path('<str:pk>/progress/', TaskProgressView.as_view(), name='task_progress'),
    path('<str:pk>/progress', TaskProgressView.as_view(), name='task_progress_no_slash'),

    # Task completion submission
    path('<str:pk>/complete/', TaskCompletionView.as_view(), name='task_complete'),
    path('<str:pk>/complete', TaskCompletionView.as_view(), name='task_complete_no_slash'),

    # Administrative sign-off (verify & resolve)
    path('<str:pk>/verify-resolve/', TaskVerifyResolveView.as_view(), name='task_verify_resolve'),
    path('<str:pk>/verify-resolve', TaskVerifyResolveView.as_view(), name='task_verify_resolve_no_slash'),

    # Administrative return / reject
    path('<str:pk>/return-reject/', TaskReturnRejectView.as_view(), name='task_return_reject'),
    path('<str:pk>/return-reject', TaskReturnRejectView.as_view(), name='task_return_reject_no_slash'),

    # Single task detail & reassign
    path('<str:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('<str:pk>', TaskDetailView.as_view(), name='task_detail_no_slash'),

    # List tasks
    path('', TaskListCreateView.as_view(), name='task_list_create'),
]
