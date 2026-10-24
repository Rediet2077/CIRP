import uuid
from rest_framework import serializers
from .models import StaffContractor
from apps.departments.models import Department
from utils.enums import TaskStatus, StaffRoleType


class StaffContractorSerializer(serializers.ModelSerializer):
    """
    Serializer conforming strictly to React Admin's StaffContractorRecordSchema.
    """
    department_id = serializers.UUIDField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    contractor_company = serializers.CharField(source='contractor_company_name', read_only=True)
    active_tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    overdue_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = StaffContractor
        fields = [
            'id',
            'name',
            'phone_number',
            'email',
            'department_id',
            'department_name',
            'role_type',
            'position_title',
            'specialization',
            'is_contractor',
            'contractor_company',
            'contractor_company_name',
            'license_number',
            'active_tasks_count',
            'completed_tasks_count',
            'overdue_tasks_count',
            'performance_score',
            'is_available',
        ]

    def get_active_tasks_count(self, obj) -> int:
        return obj.assigned_tasks.filter(
            status__in=[TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]
        ).count()

    def get_completed_tasks_count(self, obj) -> int:
        return obj.assigned_tasks.filter(
            status__in=[TaskStatus.RESOLVED, TaskStatus.VERIFIED]
        ).count()

    def get_overdue_tasks_count(self, obj) -> int:
        count = 0
        for task in obj.assigned_tasks.all():
            if task.is_overdue:
                count += 1
        return count


class CreateStaffContractorSerializer(serializers.ModelSerializer):
    """
    Serializer for provisioning staff or external contractor profiles.
    Enforces required company name and license when is_contractor=True.
    """
    department_id = serializers.CharField(write_only=True)
    phone = serializers.CharField(source='phone_number', required=False)
    contractor_company = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = StaffContractor
        fields = [
            'id',
            'name',
            'phone_number',
            'phone',
            'email',
            'department_id',
            'role_type',
            'position_title',
            'specialization',
            'is_contractor',
            'contractor_company',
            'contractor_company_name',
            'license_number',
            'performance_score',
            'is_available',
        ]
        read_only_fields = ['id']

    def validate_department_id(self, value):
        try:
            val_uuid = uuid.UUID(str(value))
            dept = Department.objects.filter(id=val_uuid).first()
        except (ValueError, TypeError):
            dept = Department.objects.filter(code__iexact=str(value).strip()).first()

        if not dept:
            raise serializers.ValidationError(f"Department '{value}' not found.")
        return dept

    def validate(self, attrs):
        # Support phone or phone_number
        if 'phone_number' not in attrs and 'phone' in attrs:
            attrs['phone_number'] = attrs.pop('phone')

        if not attrs.get('contractor_company_name') and attrs.get('contractor_company'):
            attrs['contractor_company_name'] = attrs.pop('contractor_company')
        elif 'contractor_company' in attrs:
            attrs.pop('contractor_company')

        is_contractor = attrs.get('is_contractor', False)
        company = attrs.get('contractor_company_name', '').strip()
        license_num = attrs.get('license_number', '').strip()

        if is_contractor:
            if not company:
                raise serializers.ValidationError({
                    "contractor_company_name": "Company name is required for external contractors."
                })
            if not license_num:
                raise serializers.ValidationError({
                    "license_number": "License number is required for external contractors."
                })

        return attrs

    def create(self, validated_data):
        dept = validated_data.pop('department_id')
        validated_data['department'] = dept
        return super().create(validated_data)
