import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable system-wide audit log for officer actions and lifecycle events.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    officer_name = models.CharField(max_length=150, blank=True, default='System')
    officer_role = models.CharField(max_length=50, blank=True, default='SYSTEM')
    department_name = models.CharField(max_length=150, blank=True, default='Central Operations')

    action_type = models.CharField(max_length=100, db_index=True)
    target_entity_type = models.CharField(max_length=50) # REPORT, TASK, ASSET, EXTENSION, DEPARTMENT
    target_code = models.CharField(max_length=100)

    summary = models.CharField(max_length=255)
    details = models.TextField(blank=True, default='')

    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.officer_name} - {self.action_type} on {self.target_code}"
