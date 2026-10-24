import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from utils.enums import UserRole


class UserManager(BaseUserManager):
    """
    Custom user manager supporting email-based authentication and role initialization.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.SYSTEM_ADMIN)
        extra_fields.setdefault('status', 'ACTIVE')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model unifying Flutter citizens and React administration officers.
    """
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        PENDING = 'PENDING', 'Pending'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone_number = models.CharField(max_length=30, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')

    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CITIZEN,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )

    # Department reference for Department Admins and staff officers
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )

    preferred_language = models.CharField(max_length=20, default='en')
    profile_image_url = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['-created_at']

    @property
    def is_system_admin(self) -> bool:
        return bool(self.role == UserRole.SYSTEM_ADMIN or self.is_superuser)

    def get_full_name(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email

    def get_short_name(self) -> str:
        return self.first_name if self.first_name else self.email

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
