import uuid
from django.db import models
from django.utils import timezone
from utils.enums import TaskPriority, TaskStatus


class Task(models.Model):
    """
    Work order assigned to technician or contractor team following report acceptance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_code = models.CharField(max_length=50, unique=True, db_index=True)

    report = models.OneToOneField(
        'reports.Report',
        on_delete=models.CASCADE,
        related_name='task'
    )
    department = models.ForeignKey(
        'departments.Department',
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    assigned_worker = models.ForeignKey(
        'contractors.StaffContractor',
        on_delete=models.PROTECT,
        related_name='assigned_tasks'
    )

    work_description = models.TextField()
    internal_note = models.TextField(blank=True, default='')

    priority = models.CharField(
        max_length=20,
        choices=TaskPriority.choices,
        default=TaskPriority.MEDIUM
    )
    status = models.CharField(
        max_length=40,
        choices=TaskStatus.choices,
        default=TaskStatus.ASSIGNED,
        db_index=True
    )

    progress_percentage = models.IntegerField(default=0)
    original_deadline_date = models.DateTimeField()
    deadline_date = models.DateTimeField()

    # Progress notes JSON array: [{timestamp, author, note, percentage}]
    progress_notes = models.JSONField(default=list, blank=True)

    # Completion submission: {completion_date, completion_notes, before_photos, after_photos, submitted_by}
    completion_submission = models.JSONField(default=dict, blank=True)

    # Rejection/Return history: [{timestamp, rejected_by, reason, required_correction, new_expected_date}]
    rejection_history = models.JSONField(default=list, blank=True)

    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_overdue(self):
        if self.status in [TaskStatus.RESOLVED, TaskStatus.VERIFIED]:
            return False
        return timezone.now() > self.deadline_date

    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        diff = timezone.now() - self.deadline_date
        return max(0, diff.days)

    def __str__(self):
        return f"{self.task_code} ({self.get_status_display()})"
