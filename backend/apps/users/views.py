from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from utils.pagination import StandardResultsSetPagination
from rest_framework.throttling import ScopedRateThrottle
import random
import string

from .models import PasswordResetOTP

from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserAdminUpdateSerializer,
    ChangePasswordSerializer,
    UserStatusUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetVerifyOTPSerializer,
    PasswordResetConfirmSerializer,
)

from utils.responses import success_response, error_response
from utils.permissions import IsSystemAdmin
from utils.audit import record_audit_log

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for citizen registration.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Record audit log for registration
        record_audit_log(
            action="USER_REGISTERED",
            entity_type="User",
            entity_id=user.id,
            actor=user,
            request=request,
            new_values={"email": user.email, "role": user.role},
            reason="Citizen self-registration."
        )

        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        payload = {
            "user": user_data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }
        return success_response(
            data=payload,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login endpoint returning user metadata.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'
    
    def post(self, request, *args, **kwargs):
        print(f"DEBUG: Login request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(f"DEBUG: Validation error: {e}")
            print(f"DEBUG: Serializer errors: {serializer.errors}")
            raise

        # Record audit log for login
        user = serializer.user
        record_audit_log(
            action="USER_LOGGED_IN",
            entity_type="User",
            entity_id=user.id,
            actor=user,
            request=request,
            reason="User logged in via JWT credentials."
        )

        return success_response(
            data=serializer.validated_data,
            message="Authentication successful."
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Authenticated endpoint to view and update the logged-in user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data, message="Profile retrieved successfully.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_data = {"first_name": instance.first_name, "last_name": instance.last_name}

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Record audit log for profile update
        record_audit_log(
            action="PROFILE_UPDATED",
            entity_type="User",
            entity_id=instance.id,
            actor=instance,
            request=request,
            old_values=old_data,
            new_values={"first_name": instance.first_name, "last_name": instance.last_name},
            reason="User updated their profile details."
        )

        return success_response(data=serializer.data, message="Profile updated successfully.")


class UserListView(generics.ListAPIView):
    """
    System Admin only: List and filter platform users.
    """
    serializer_class = UserSerializer
    permission_classes = [IsSystemAdmin]
    pagination_class = StandardResultsSetPagination
    queryset = User.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_verified', 'preferred_language']
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['created_at', 'email', 'role']



class UserDetailAdminView(generics.RetrieveUpdateAPIView):
    """
    System Admin only: Retrieve user details or update role/status.
    """
    permission_classes = [IsSystemAdmin]
    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserAdminUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data, message="User details retrieved successfully.")

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_values = {
            "role": instance.role,
            "is_active": instance.is_active,
            "is_verified": instance.is_verified,
        }

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_values = {
            "role": instance.role,
            "is_active": instance.is_active,
            "is_verified": instance.is_verified,
        }

        # Record audit log for admin user modification
        record_audit_log(
            action="USER_ADMIN_MODIFIED",
            entity_type="User",
            entity_id=instance.id,
            actor=request.user,
            request=request,
            old_values=old_values,
            new_values=new_values,
            reason=f"Admin modified user status/role to {instance.role}."
        )

        return success_response(
            data=UserSerializer(instance).data,
            message="User role/status updated successfully."
        )

class ChangePasswordView(generics.GenericAPIView):
    """
    Authenticated endpoint allowing users to change their password securely.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')

        if not user.check_password(old_password):
            return error_response(
                message="Invalid credentials.",
                errors={"old_password": ["Current password is incorrect."]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        # Record audit log for security credential change
        record_audit_log(
            action="PASSWORD_CHANGED",
            entity_type="User",
            entity_id=user.id,
            actor=user,
            request=request,
            reason="User successfully changed account password."
        )

        return success_response(
            message="Password changed successfully. Please authenticate with your new password."
        )


class UserStatusUpdateView(generics.UpdateAPIView):
    """
    System Admin only: Explicitly toggle account activation or verification status.
    """
    serializer_class = UserStatusUpdateSerializer
    permission_classes = [IsSystemAdmin]
    queryset = User.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        old_values = {
            "is_active": instance.is_active,
            "is_verified": instance.is_verified,
        }

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        new_values = {
            "is_active": instance.is_active,
            "is_verified": instance.is_verified,
        }

        # Record audit log for administrative status toggle
        record_audit_log(
            action="USER_STATUS_TOGGLED",
            entity_type="User",
            entity_id=instance.id,
            actor=request.user,
            request=request,
            old_values=old_values,
            new_values=new_values,
            reason=f"Admin updated active/verified flags for {instance.email}."
        )

        return success_response(
            data=UserSerializer(instance).data,
            message="User account status updated successfully."
        )



class PasswordResetRequestView(generics.GenericAPIView):
    """
    Public endpoint to request password reset. Sends OTP to email.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))

        # Save OTP to database
        PasswordResetOTP.objects.create(
            email=email,
            otp=otp
        )

        # Send OTP via email
        try:
            send_mail(
                subject='CIRP - Password Reset OTP',
                message=f'Your password reset OTP is: {otp}\n\nThis code will expire in 10 minutes.\n\nIf you did not request a password reset, please ignore this email.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cirp.com'),
                recipient_list=[email],
                fail_silently=False,
            )
            
            # Record audit log
            record_audit_log(
                action="PASSWORD_RESET_REQUESTED",
                entity_type="User",
                entity_id=user.id,
                actor=user,
                request=request,
                reason=f"Password reset OTP sent to {email}."
            )

            return success_response(
                message=f"Password reset OTP has been sent to {email}."
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
            # For development, return OTP in response
            return success_response(
                message=f"OTP generated (email not configured): {otp}",
                data={"otp": otp, "email": email}
            )


class PasswordResetVerifyOTPView(generics.GenericAPIView):
    """
    Public endpoint to verify OTP code without resetting password.
    """
    serializer_class = PasswordResetVerifyOTPSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        # Find valid OTP
        try:
            otp_record = PasswordResetOTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False
            ).latest('created_at')

            if not otp_record.is_valid():
                return error_response(
                    message="OTP has expired. Please request a new one.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            return success_response(
                message="OTP verified successfully. You can now reset your password."
            )

        except PasswordResetOTP.DoesNotExist:
            return error_response(
                message="Invalid OTP code.",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    Public endpoint to reset password using OTP.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'auth'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        # Find valid OTP
        try:
            otp_record = PasswordResetOTP.objects.filter(
                email=email,
                otp=otp,
                is_used=False
            ).latest('created_at')

            if not otp_record.is_valid():
                return error_response(
                    message="OTP has expired. Please request a new one.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Mark OTP as used
            otp_record.is_used = True
            otp_record.save()

            # Update user password
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # Record audit log
            record_audit_log(
                action="PASSWORD_RESET_COMPLETED",
                entity_type="User",
                entity_id=user.id,
                actor=user,
                request=request,
                reason=f"Password successfully reset via OTP for {email}."
            )

            return success_response(
                message="Password has been reset successfully. You can now login with your new password."
            )

        except PasswordResetOTP.DoesNotExist:
            return error_response(
                message="Invalid OTP code.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
