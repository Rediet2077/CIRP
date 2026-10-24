import uuid
from django.db import models
from utils.enums import StaffRoleType


class StaffContractor(models.Model):
    """
    Staff technicians, maintenance officers, and external contractor teams.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField(max_length=255)

    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='contractors_and_staff'
    )

    role_type = models.CharField(
        max_length=30,
        choices=StaffRoleType.choices,
        default=StaffRoleType.FIELD_TECHNICIAN
    )
    position_title = models.CharField(max_length=100, blank=True, default='Technician')
    specialization = models.CharField(max_length=150, blank=True, default='General Repair')

    is_contractor = models.BooleanField(default=False)
    contractor_company_name = models.CharField(max_length=150, blank=True, default='')
    license_number = models.CharField(max_length=100, blank=True, default='')

    performance_score = models.FloatField(default=95.0)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_role_type_display()})"
