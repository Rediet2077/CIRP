import uuid
from django.db import models
from django.conf import settings
from utils.enums import DisputeStatus


class Dispute(models.Model):
    """
    Citizen appeal/dispute challenging report rejection or unsatisfactory resolution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        'reports.Report',
        on_delete=models.CASCADE,
        related_name='disputes'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disputes_submitted'
    )

    reason = models.TextField()
    evidence_photos = models.JSONField(default=list, blank=True)

    status = models.CharField(
        max_length=20,
        choices=DisputeStatus.choices,
        default=DisputeStatus.OPEN,
        db_index=True
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_reviewed'
    )
    review_notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Dispute on {self.report.report_code} ({self.get_status_display()})"
