import uuid
from rest_framework import serializers
from .models import Task
from apps.contractors.models import StaffContractor
from utils.enums import TaskPriority, TaskStatus


class TaskSerializer(serializers.ModelSerializer):
    """
    Task record serializer strictly conforming to React Admin's TaskRecordSchema.
    """
    report_id = serializers.UUIDField(source='report.id', read_only=True)
    report_code = serializers.CharField(source='report.report_code', read_only=True)
    asset_id = serializers.SerializerMethodField()
    asset_code = serializers.SerializerMethodField()
    asset_type_label = serializers.SerializerMethodField()
    department_id = serializers.UUIDField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    assigned_worker_id = serializers.UUIDField(source='assigned_worker.id', read_only=True)
    assigned_worker_name = serializers.CharField(source='assigned_worker.name', read_only=True)
    is_contractor = serializers.BooleanField(source='assigned_worker.is_contractor', read_only=True)
    contractor_company = serializers.CharField(source='assigned_worker.contractor_company_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    extensions = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'task_code',
            'report_id',
            'report_code',
            'asset_id',
            'asset_code',
            'asset_type_label',
            'department_id',
            'department_name',
            'assigned_worker_id',
            'assigned_worker_name',
            'is_contractor',
            'contractor_company',
            'work_description',
            'internal_note',
            'priority',
            'status',
            'progress_percentage',
            'created_at',
            'deadline_date',
            'original_deadline_date',
            'is_overdue',
            'days_overdue',
            'progress_notes',
            'completion_submission',
            'rejection_history',
            'extensions',
        ]
        read_only_fields = ['id', 'created_at']

    def get_asset_id(self, obj):
        if obj.report and obj.report.asset:
            return str(obj.report.asset.id)
        return "unassigned"

    def get_asset_code(self, obj):
        if obj.report and obj.report.asset:
            return obj.report.asset.asset_code
        return "GENERAL-INFRA"

    def get_asset_type_label(self, obj):
        if obj.report and obj.report.asset and obj.report.asset.asset_type:
            return obj.report.asset.asset_type.name
        return "General Infrastructure"

    def get_extensions(self, obj):
        from apps.extensions.serializers import ExtensionSerializer
        return ExtensionSerializer(obj.extensions.all(), many=True).data


class UpdateTaskProgressSerializer(serializers.Serializer):
    """
    Validates progress tracking updates.
    """
    taskId = serializers.CharField(required=False)
    task_id = serializers.CharField(required=False)
    progressPercentage = serializers.IntegerField(min_value=0, max_value=100, required=False)
    progress_percentage = serializers.IntegerField(min_value=0, max_value=100, required=False)
    newStatus = serializers.ChoiceField(
        choices=["ASSIGNED", "IN_PROGRESS", "COMPLETED_PENDING_VERIFICATION", "RESOLVED", "RETURNED"],
        required=False
    )
    new_status = serializers.ChoiceField(
        choices=["ASSIGNED", "IN_PROGRESS", "COMPLETED_PENDING_VERIFICATION", "RESOLVED", "RETURNED"],
        required=False
    )
    progressNote = serializers.CharField(min_length=1, required=False)
    progress_note = serializers.CharField(min_length=1, required=False)
    authorName = serializers.CharField(min_length=1, required=False)
    author_name = serializers.CharField(min_length=1, required=False)

    def validate(self, attrs):
        pct = attrs.get('progressPercentage') if attrs.get('progressPercentage') is not None else attrs.get('progress_percentage')
        status_val = attrs.get('newStatus') or attrs.get('new_status')
        note = attrs.get('progressNote') or attrs.get('progress_note')
        author = attrs.get('authorName') or attrs.get('author_name')

        if pct is None:
            raise serializers.ValidationError({"progressPercentage": "Progress percentage (0-100) is required."})
        if not status_val:
            raise serializers.ValidationError({"newStatus": "New status is required."})
        if not note:
            raise serializers.ValidationError({"progressNote": "Progress note is required."})
        if not author:
            raise serializers.ValidationError({"authorName": "Author name is required."})

        attrs['resolved_percentage'] = pct
        attrs['resolved_status'] = status_val
        attrs['resolved_note'] = note
        attrs['resolved_author'] = author
        return attrs


class SubmitTaskCompletionSerializer(serializers.Serializer):
    """
    Validates contractor submission of completed work.
    """
    taskId = serializers.CharField(required=False)
    task_id = serializers.CharField(required=False)
    completionNotes = serializers.CharField(min_length=1, required=False)
    completion_notes = serializers.CharField(min_length=1, required=False)
    completionDate = serializers.CharField(required=False)
    completion_date = serializers.CharField(required=False)
    beforePhotos = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    before_photos = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    afterPhotos = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    after_photos = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    submittedBy = serializers.CharField(min_length=1, required=False)
    submitted_by = serializers.CharField(min_length=1, required=False)

    def validate(self, attrs):
        notes = attrs.get('completionNotes') or attrs.get('completion_notes')
        c_date = attrs.get('completionDate') or attrs.get('completion_date')
        submitter = attrs.get('submittedBy') or attrs.get('submitted_by')
        before = attrs.get('beforePhotos') or attrs.get('before_photos', [])
        after = attrs.get('afterPhotos') or attrs.get('after_photos', [])

        if not notes:
            raise serializers.ValidationError({"completionNotes": "Completion notes are required."})
        if not c_date:
            raise serializers.ValidationError({"completionDate": "Completion date is required."})
        if not submitter:
            raise serializers.ValidationError({"submittedBy": "Submitted by name is required."})

        attrs['resolved_notes'] = notes
        attrs['resolved_date'] = c_date
        attrs['resolved_submitter'] = submitter
        attrs['resolved_before_photos'] = before
        attrs['resolved_after_photos'] = after
        return attrs


class VerifyResolveTaskSerializer(serializers.Serializer):
    """
    Validates administrative inspection, verification, and final sign-off.
    """
    taskId = serializers.CharField(required=False)
    task_id = serializers.CharField(required=False)
    officerName = serializers.CharField(min_length=1, required=False)
    officer_name = serializers.CharField(min_length=1, required=False)
    resolutionNotes = serializers.CharField(min_length=1, required=False)
    resolution_notes = serializers.CharField(min_length=1, required=False)

    def validate(self, attrs):
        officer = attrs.get('officerName') or attrs.get('officer_name')
        notes = attrs.get('resolutionNotes') or attrs.get('resolution_notes')

        if not officer:
            raise serializers.ValidationError({"officerName": "Officer name is required."})
        if not notes:
            raise serializers.ValidationError({"resolutionNotes": "Resolution notes are required."})

        attrs['resolved_officer'] = officer
        attrs['resolved_notes'] = notes
        return attrs


class ReturnRejectTaskSerializer(serializers.Serializer):
    """
    Validates administrative return/rejection of substandard completion.
    """
    taskId = serializers.CharField(required=False)
    task_id = serializers.CharField(required=False)
    officerName = serializers.CharField(min_length=1, required=False)
    officer_name = serializers.CharField(min_length=1, required=False)
    reason = serializers.CharField(min_length=1, required=True)
    requiredCorrection = serializers.CharField(min_length=1, required=False)
    required_correction = serializers.CharField(min_length=1, required=False)
    newExpectedDate = serializers.DateTimeField(required=False)
    new_expected_date = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        officer = attrs.get('officerName') or attrs.get('officer_name')
        correction = attrs.get('requiredCorrection') or attrs.get('required_correction')
        new_date = attrs.get('newExpectedDate') or attrs.get('new_expected_date')

        if not officer:
            raise serializers.ValidationError({"officerName": "Officer name is required."})
        if not correction:
            raise serializers.ValidationError({"requiredCorrection": "Required correction details are required."})
        if not new_date:
            raise serializers.ValidationError({"newExpectedDate": "New expected completion date is required."})

        attrs['resolved_officer'] = officer
        attrs['resolved_correction'] = correction
        attrs['resolved_new_date'] = new_date
        return attrs


class TaskReassignUpdateSerializer(serializers.Serializer):
    """
    Validates task update / reassigning worker / changing priority.
    """
    assignedWorkerId = serializers.CharField(required=False)
    assigned_worker_id = serializers.CharField(required=False)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, required=False)
    workDescription = serializers.CharField(required=False)
    work_description = serializers.CharField(required=False)
    internalNote = serializers.CharField(required=False, allow_blank=True)
    internal_note = serializers.CharField(required=False, allow_blank=True)
    deadlineDate = serializers.DateTimeField(required=False)
    deadline_date = serializers.DateTimeField(required=False)

    def validate(self, attrs):
        worker_id = attrs.get('assignedWorkerId') or attrs.get('assigned_worker_id')
        if worker_id:
            try:
                val_uuid = uuid.UUID(str(worker_id))
                worker = StaffContractor.objects.get(id=val_uuid)
            except (StaffContractor.DoesNotExist, ValueError):
                raise serializers.ValidationError({"assignedWorkerId": f"Worker '{worker_id}' does not exist."})
            attrs['resolved_worker'] = worker

        attrs['resolved_priority'] = attrs.get('priority')
        attrs['resolved_work_desc'] = attrs.get('workDescription') or attrs.get('work_description')
        attrs['resolved_internal_note'] = attrs.get('internalNote') if attrs.get('internalNote') is not None else attrs.get('internal_note')
        attrs['resolved_deadline'] = attrs.get('deadlineDate') or attrs.get('deadline_date')
        return attrs
