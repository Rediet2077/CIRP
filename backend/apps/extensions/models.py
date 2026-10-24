import uuid
from django.db import models
from django.conf import settings
from utils.enums import TaskExtensionStatus


class Extension(models.Model):
    """
    Formal SLA deadline extension request submitted by assigned technicians or contractors.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='extensions'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requested_extensions'
    )
    requested_by_name = models.CharField(max_length=150, blank=True, default='')

    original_deadline = models.DateTimeField()
    requested_new_deadline = models.DateTimeField()

    reason_category = models.CharField(max_length=150)
    detailed_explanation = models.TextField()
    supporting_evidence_note = models.TextField(blank=True, default='')

    status = models.CharField(
        max_length=20,
        choices=TaskExtensionStatus.choices,
        default=TaskExtensionStatus.PENDING,
        db_index=True
    )

    decision_date = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decided_extensions'
    )
    decided_by_name = models.CharField(max_length=150, blank=True, default='')
    decision_comment = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Extension for Task {self.task.task_code} ({self.get_status_display()})"
