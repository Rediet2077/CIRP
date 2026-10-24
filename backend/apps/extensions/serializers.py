import uuid
from rest_framework import serializers
from .models import Extension
from apps.tasks.models import Task
from utils.enums import TaskExtensionStatus


ALLOWED_EXTENSION_REASONS = [
    "Waiting for spare parts",
    "Severe weather / Environmental condition",
    "Specialized equipment delivery delay",
    "Access / Obstruction clearance required",
    "Additional technician crew needed",
]


class ExtensionSerializer(serializers.ModelSerializer):
    """
    Serializer strictly conforming to React Admin's ExtensionRecordSchema.
    """
    task_id = serializers.UUIDField(source='task.id', read_only=True)
    task_code = serializers.CharField(source='task.task_code', read_only=True)
    report_code = serializers.SerializerMethodField()
    asset_code = serializers.SerializerMethodField()
    department_id = serializers.UUIDField(source='task.department.id', read_only=True)
    original_deadline = serializers.SerializerMethodField()
    requested_new_deadline = serializers.SerializerMethodField()
    requested_by = serializers.SerializerMethodField()
    requested_at = serializers.SerializerMethodField()
    decision_date = serializers.SerializerMethodField()
    decided_by = serializers.SerializerMethodField()

    class Meta:
        model = Extension
        fields = [
            'id',
            'task_id',
            'task_code',
            'report_code',
            'asset_code',
            'department_id',
            'original_deadline',
            'requested_new_deadline',
            'reason_category',
            'detailed_explanation',
            'supporting_evidence_note',
            'requested_by',
            'requested_at',
            'status',
            'decision_date',
            'decided_by',
            'decision_comment',
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def get_report_code(self, obj) -> str:
        if obj.task and obj.task.report:
            return obj.task.report.report_code
        return "GENERAL-INCIDENT"

    def get_asset_code(self, obj) -> str:
        if obj.task and obj.task.report and obj.task.report.asset:
            return obj.task.report.asset.asset_code
        return "GENERAL-INFRA"

    def get_original_deadline(self, obj) -> str:
        return obj.original_deadline.isoformat() if obj.original_deadline else ""

    def get_requested_new_deadline(self, obj) -> str:
        return obj.requested_new_deadline.isoformat() if obj.requested_new_deadline else ""

    def get_requested_by(self, obj) -> str:
        if obj.requested_by_name:
            return obj.requested_by_name
        if obj.requested_by:
            return obj.requested_by.get_full_name()
        return "Field Worker"

    def get_requested_at(self, obj) -> str:
        return obj.created_at.isoformat() if obj.created_at else ""

    def get_decision_date(self, obj) -> str | None:
        return obj.decision_date.isoformat() if obj.decision_date else None

    def get_decided_by(self, obj) -> str | None:
        if obj.decided_by_name:
            return obj.decided_by_name
        if obj.decided_by:
            return obj.decided_by.get_full_name()
        return None


class RequestExtensionSerializer(serializers.Serializer):
    """
    Validates input for requesting a deadline extension from React Admin or Contractor app.
    """
    taskId = serializers.CharField(required=False)
    task_id = serializers.CharField(required=False)
    requestedNewDeadline = serializers.DateTimeField(required=False)
    requested_new_deadline = serializers.DateTimeField(required=False)
    reasonCategory = serializers.ChoiceField(choices=ALLOWED_EXTENSION_REASONS, required=False)
    reason_category = serializers.ChoiceField(choices=ALLOWED_EXTENSION_REASONS, required=False)
    detailedExplanation = serializers.CharField(min_length=1, required=False)
    detailed_explanation = serializers.CharField(min_length=1, required=False)
    supportingEvidenceNote = serializers.CharField(required=False, allow_blank=True, default='')
    supporting_evidence_note = serializers.CharField(required=False, allow_blank=True, default='')
    requestedBy = serializers.CharField(required=False, allow_blank=True)
    requested_by = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        task_id = attrs.get('taskId') or attrs.get('task_id')
        new_deadline = attrs.get('requestedNewDeadline') or attrs.get('requested_new_deadline')
        reason_cat = attrs.get('reasonCategory') or attrs.get('reason_category')
        explanation = attrs.get('detailedExplanation') or attrs.get('detailed_explanation')
        evidence = attrs.get('supportingEvidenceNote') or attrs.get('supporting_evidence_note', '')
        requester_name = attrs.get('requestedBy') or attrs.get('requested_by', '')

        if not task_id:
            raise serializers.ValidationError({"taskId": "Task ID is required."})
        if not new_deadline:
            raise serializers.ValidationError({"requestedNewDeadline": "Requested new deadline date is required."})
        if not reason_cat:
            raise serializers.ValidationError({"reasonCategory": "Reason category is required."})
        if not explanation:
            raise serializers.ValidationError({"detailedExplanation": "Detailed explanation is required."})

        # Resolve Task
        try:
            val_uuid = uuid.UUID(str(task_id))
            task = Task.objects.get(id=val_uuid)
        except (Task.DoesNotExist, ValueError):
            try:
                task = Task.objects.get(task_code=str(task_id))
            except Task.DoesNotExist:
                raise serializers.ValidationError({"taskId": f"Task '{task_id}' not found."})

        # Validate that new deadline is after the current deadline
        if new_deadline <= task.deadline_date:
            raise serializers.ValidationError({
                "requestedNewDeadline": "Requested new deadline must be strictly after the current deadline."
            })

        attrs['resolved_task'] = task
        attrs['resolved_new_deadline'] = new_deadline
        attrs['resolved_reason_category'] = reason_cat
        attrs['resolved_explanation'] = explanation
        attrs['resolved_evidence'] = evidence
        attrs['resolved_requester_name'] = requester_name
        return attrs


class DecideExtensionSerializer(serializers.Serializer):
    """
    Validates administrative approval or rejection of a deadline extension.
    """
    extensionId = serializers.CharField(required=False)
    extension_id = serializers.CharField(required=False)
    approve = serializers.BooleanField(required=True)
    decidedBy = serializers.CharField(required=False, allow_blank=True)
    decided_by = serializers.CharField(required=False, allow_blank=True)
    decisionComment = serializers.CharField(required=False, allow_blank=True, default='')
    decision_comment = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        ext_id = attrs.get('extensionId') or attrs.get('extension_id')
        decider_name = attrs.get('decidedBy') or attrs.get('decided_by', '')
        comment = attrs.get('decisionComment') or attrs.get('decision_comment', '')

        attrs['resolved_decider_name'] = decider_name
        attrs['resolved_comment'] = comment
        return attrs
