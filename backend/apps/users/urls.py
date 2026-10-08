from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileView,
    UserListView,
    UserDetailAdminView,
    ChangePasswordView,
    UserStatusUpdateView,
    PasswordResetRequestView,
    PasswordResetVerifyOTPView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Authentication Endpoints
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'),
    
    # Password Reset Endpoints
    path('auth/password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/verify/', PasswordResetVerifyOTPView.as_view(), name='password_reset_verify'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Profile Endpoints
    path('users/me/', UserProfileView.as_view(), name='user_profile'),

    # Administrative User Management Endpoints
    path('users/', UserListView.as_view(), name='admin_user_list'),
    path('users/<uuid:id>/', UserDetailAdminView.as_view(), name='admin_user_detail'),
    path('users/<uuid:id>/status/', UserStatusUpdateView.as_view(), name='admin_user_status_update'),
]