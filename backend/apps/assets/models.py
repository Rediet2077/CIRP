import uuid
from django.db import models
from django.conf import settings
from utils.enums import AssetStatus, AssetCondition


class AssetType(models.Model):
    """
    Standard types of physical municipal infrastructure.
    """
    id = models.CharField(max_length=50, primary_key=True) # e.g. 'street_light', 'road'
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    responsible_department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_asset_types'
    )
    requires_location = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Asset(models.Model):
    """
    Physical municipal assets with geographic coordinates and technical specifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset_code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')

    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT, related_name='assets')
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='assets')

    status = models.CharField(
        max_length=30,
        choices=AssetStatus.choices,
        default=AssetStatus.ACTIVE,
        db_index=True
    )
    condition = models.CharField(
        max_length=20,
        choices=AssetCondition.choices,
        default=AssetCondition.GOOD
    )

    installation_date = models.DateField(null=True, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)

    # Standard numerical GPS coordinates (avoids Windows C-extension GDAL issues)
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    address = models.CharField(max_length=255, blank=True, default='')
    landmark = models.CharField(max_length=255, blank=True, default='')

    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_assets'
    )

    # Technical specifications stored as structured JSON (e.g. pole material, wattage, width)
    specific_data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset_code} - {self.name}"
