from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CitizenRegisterView,
    DepartmentApplyView,
    CustomTokenObtainPairView,
    UserProfileView,
    ChangePasswordView,
    UserListView,
    UserDetailView,
)

urlpatterns = [
    # Auth endpoints
    re_path(r'^auth/register/?$', CitizenRegisterView.as_view(), name='auth_register'),
    re_path(r'^auth/login/?$', CustomTokenObtainPairView.as_view(), name='auth_login'),
    re_path(r'^auth/token/refresh/?$', TokenRefreshView.as_view(), name='auth_token_refresh'),
    re_path(r'^auth/change-password/?$', ChangePasswordView.as_view(), name='auth_change_password'),
    re_path(r'^auth/department-signup/?$', DepartmentApplyView.as_view(), name='auth_department_signup'),

    # React Admin department onboarding application alias
    re_path(r'^departments/apply/?$', DepartmentApplyView.as_view(), name='departments_apply'),

    # User profile & moderation endpoints
    re_path(r'^users/me/update/?$', UserProfileView.as_view(), name='users_me_update'),
    re_path(r'^users/me/?$', UserProfileView.as_view(), name='users_me'),
    re_path(r'^users/(?P<id>[0-9a-f-]+)/?$', UserDetailView.as_view(), name='user_detail'),
    re_path(r'^users/?$', UserListView.as_view(), name='users_list'),
]
