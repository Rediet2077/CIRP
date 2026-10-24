from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.enums import UserRole
from apps.departments.models import Department
from apps.departments.serializers import DepartmentRefSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer matching React UserRecordSchema and Flutter user profile.
    """
    department = DepartmentRefSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'role',
            'role_display',
            'status',
            'department',
            'preferred_language',
            'profile_image_url',
            'is_active',
            'is_verified',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'role', 'status', 'is_active', 'is_verified', 'created_at', 'updated_at']


class CitizenRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for citizen registration matching Flutter's RegisterScreen.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'password',
            'password_confirm',
            'preferred_language',
        ]

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return normalized

    def validate_phone_number(self, value):
        if value and User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("An account with this phone number already exists.")
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        # Enforce Citizen role and active status
        user = User.objects.create_user(
            password=password,
            role=UserRole.CITIZEN,
            status=User.StatusChoices.ACTIVE,
            is_active=True,
            is_verified=True,
            **validated_data
        )
        return user


class DepartmentApplicationSerializer(serializers.Serializer):
    """
    Serializer for municipal department onboarding applications from React Admin.
    Security: The applicant is stored with PENDING status and CANNOT log in until
    reviewed and approved by a System Administrator.
    """
    department_name = serializers.CharField(max_length=150)
    department_code = serializers.CharField(max_length=50)
    department_email = serializers.EmailField()
    department_phone = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)

    representative_first_name = serializers.CharField(max_length=100)
    representative_last_name = serializers.CharField(max_length=100)
    representative_email = serializers.EmailField()
    representative_phone = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_department_code(self, value):
        code = value.strip().upper()
        if Department.objects.filter(code=code).exists():
            raise serializers.ValidationError(f"Department code '{code}' is already registered.")
        return code

    def validate_representative_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user account with this representative email already exists.")
        return email

    def save(self):
        dept_code = self.validated_data['department_code']
        dept_name = self.validated_data['department_name']

        # 1. Create the Department in PENDING status
        dept = Department.objects.create(
            name=dept_name,
            code=dept_code,
            contact_email=self.validated_data['department_email'],
            contact_phone=self.validated_data['department_phone'],
            office_location=self.validated_data['address'],
            approval_status=Department.ApprovalStatus.PENDING,
            is_active=False
        )

        # 2. Create the Department Admin user in PENDING status
        user = User.objects.create_user(
            email=self.validated_data['representative_email'],
            password=self.validated_data['password'],
            first_name=self.validated_data['representative_first_name'],
            last_name=self.validated_data['representative_last_name'],
            phone_number=self.validated_data['representative_phone'],
            role=UserRole.DEPARTMENT_ADMIN,
            status=User.StatusChoices.PENDING,
            department=dept,
            is_active=False,
            is_verified=False
        )

        dept.admin_user = user
        dept.save(update_fields=['admin_user'])

        return dept


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT login serializer ensuring compatibility with both:
    1. React Admin: returns { access, refresh, user: { id, email, first_name, last_name, role, status, department } }
    2. Flutter Mobile: returns { access, refresh, tokens: { access, refresh }, user: { ... } }
    """
    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user
        if not user.is_active or user.status != User.StatusChoices.ACTIVE:
            raise serializers.ValidationError(
                "Your account is pending administrative approval or has been deactivated."
            )

        user_data = UserSerializer(user).data
        data['user'] = user_data
        data['tokens'] = {
            'access': data['access'],
            'refresh': data['refresh'],
        }
        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating authenticated citizen profile details.
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'preferred_language',
            'profile_image_url',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "New passwords do not match."})
        return attrs
