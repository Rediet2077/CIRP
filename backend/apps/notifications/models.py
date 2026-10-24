import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    In-app and system alert notifications for Citizens and Department Admins.
    """
    class Category(models.TextChoices):
        ESCALATION = 'ESCALATION', 'Escalation'
        NEW_REPORT = 'NEW_REPORT', 'New Report'
        EXTENSION_REQUEST = 'EXTENSION_REQUEST', 'Extension Request'
        TASK_COMPLETED = 'TASK_COMPLETED', 'Task Completed'
        SYSTEM_ALERT = 'SYSTEM_ALERT', 'System Alert'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        CRITICAL = 'CRITICAL', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(max_length=255)
    message = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.SYSTEM_ALERT
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.LOW
    )

    is_read = models.BooleanField(default=False, db_index=True)
    target_url = models.CharField(max_length=255, blank=True, default='')

    # Optional department scoping
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    entity_code = models.CharField(max_length=100, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.email}"
