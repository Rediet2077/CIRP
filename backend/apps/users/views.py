from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model

from utils.responses import api_response, error_response
from utils.permissions import IsSystemAdmin
from .serializers import (
    UserSerializer,
    CitizenRegisterSerializer,
    DepartmentApplicationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class CitizenRegisterView(APIView):
    """
    Citizen self-registration endpoint supporting Flutter Mobile app.
    POST /api/v1/auth/register/
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CitizenRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Registration failed. Please correct the highlighted errors.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        payload = {
            "user": user_data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        }

        return api_response(
            data=payload,
            message="Registration successful",
            status_code=status.HTTP_201_CREATED,
            request=request,
            force_envelope=True  # Flutter expects {success: true, message: ..., data: ...}
        )


class DepartmentApplyView(APIView):
    """
    Department registration/application endpoint supporting React Admin dashboard.
    POST /api/v1/departments/apply/ and POST /api/v1/auth/department-signup/
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = DepartmentApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Application failed. Please verify the submitted information.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

        serializer.save()

        # Matches React SignupResponseSchema: { message: string }
        return api_response(
            data={"message": "Department application submitted successfully. Awaiting approval."},
            message="Department application submitted successfully. Awaiting approval.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Dual-compatible JWT login endpoint for React Admin and Flutter Mobile.
    POST /api/v1/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            return error_response(
                message="Invalid email or password.",
                errors=getattr(exc, 'detail', {'detail': str(exc)}),
                status_code=status.HTTP_401_UNAUTHORIZED,
                request=request
            )

        return api_response(
            data=serializer.validated_data,
            message="Login successful",
            status_code=status.HTTP_200_OK,
            request=request
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Profile retrieval and update endpoint for authenticated users.
    GET /api/v1/users/me/
    PATCH /api/v1/users/me/ (or /api/v1/users/me/update/)
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return api_response(
            data=serializer.data,
            message="Profile retrieved successfully.",
            request=request
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        updated_data = UserSerializer(instance).data
        return api_response(
            data=updated_data,
            message="Profile updated successfully.",
            request=request
        )


class ChangePasswordView(APIView):
    """
    Secure password change endpoint for authenticated users.
    POST /api/v1/auth/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Password change failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

        user = request.user
        old_password = serializer.validated_data['old_password']
        if not user.check_password(old_password):
            return error_response(
                message="Current password is incorrect.",
                errors={"old_password": ["Current password is incorrect."]},
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return api_response(
            data={"message": "Password changed successfully."},
            message="Password changed successfully.",
            request=request
        )


class UserListView(generics.ListAPIView):
    """
    System Admin endpoint to list all platform users.
    GET /api/v1/users/
    """
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]
    queryset = User.objects.all().select_related('department').order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'is_active', 'department']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['created_at', 'email', 'role']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Matches React UserListResponseSchema: z.array(UserRecordSchema)
        return api_response(
            data=serializer.data,
            message="Users retrieved successfully.",
            request=request
        )


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    System Admin endpoint to retrieve or update a specific user.
    GET /api/v1/users/<uuid>/
    PATCH /api/v1/users/<uuid>/
    """
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]
    queryset = User.objects.all().select_related('department')
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            data=serializer.data,
            message="User retrieved successfully.",
            request=request
        )
