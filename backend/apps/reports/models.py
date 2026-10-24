import uuid
from django.db import models
from django.conf import settings
from utils.enums import ReportPriority, ReportStatus


class Report(models.Model):
    """
    Infrastructure failure incident reports submitted by citizens or field officers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_code = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    # Submitting citizen (nullable if reported anonymously or publicly)
    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    citizen_name = models.CharField(max_length=150, blank=True, default='Concerned Citizen')
    citizen_contact = models.CharField(max_length=100, blank=True, default='')

    # Category & Department
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='reports'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='reports'
    )

    # Physical asset link (optional, linked by triage officer)
    asset = models.ForeignKey(
        'assets.Asset',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    # Standard numeric coordinates
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    address = models.CharField(max_length=255, blank=True, default='')
    landmark = models.CharField(max_length=255, blank=True, default='')

    priority = models.CharField(
        max_length=20,
        choices=ReportPriority.choices,
        default=ReportPriority.MEDIUM,
        db_index=True
    )
    status = models.CharField(
        max_length=40,
        choices=ReportStatus.choices,
        default=ReportStatus.NEW,
        db_index=True
    )

    # Photos uploaded with report (URLs or media paths)
    media_photos = models.JSONField(default=list, blank=True)

    # AI Microservice predictions & duplicate analysis
    ai_category_prediction = models.JSONField(default=dict, blank=True)
    ai_duplicate_analysis = models.JSONField(default=dict, blank=True)

    # Decision feedback & Resolution
    public_delay_explanation = models.TextField(blank=True, default='')
    rejection_reason = models.TextField(blank=True, default='')
    resolution_notes = models.TextField(blank=True, default='')
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Deletion scopes
    is_deleted_by_citizen = models.BooleanField(default=False)
    is_deleted_by_admin = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.report_code} - {self.title}"
