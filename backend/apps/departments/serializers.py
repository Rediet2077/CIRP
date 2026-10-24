from rest_framework import serializers
from .models import Department


class DepartmentRefSerializer(serializers.ModelSerializer):
    """
    Compact department reference matching React Admin's DepartmentRefSchema.
    """
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class DepartmentSerializer(serializers.ModelSerializer):
    """
    Full department serializer matching React Admin DepartmentRecordSchema
    and Flutter department dropdowns.
    """
    total_assets = serializers.SerializerMethodField()
    active_reports = serializers.SerializerMethodField()
    active_tasks = serializers.SerializerMethodField()
    overdue_tasks = serializers.SerializerMethodField()
    resolved_reports = serializers.SerializerMethodField()
    resolution_rate_percent = serializers.SerializerMethodField()
    avg_acceptance_hours = serializers.SerializerMethodField()
    avg_completion_days = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'description',
            'contact_email',
            'contact_phone',
            'office_location',
            'responsible_asset_types',
            'approval_status',
            'is_active',
            'total_assets',
            'active_reports',
            'active_tasks',
            'overdue_tasks',
            'resolved_reports',
            'resolution_rate_percent',
            'avg_acceptance_hours',
            'avg_completion_days',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_assets(self, obj):
        return getattr(obj, 'assets_count', obj.assets.count() if hasattr(obj, 'assets') else 0)

    def get_active_reports(self, obj):
        if hasattr(obj, 'reports'):
            return obj.reports.filter(status__in=['NEW', 'ACCEPTED', 'IN_PROGRESS']).count()
        return 0

    def get_active_tasks(self, obj):
        if hasattr(obj, 'tasks'):
            return obj.tasks.filter(status__in=['ASSIGNED', 'IN_PROGRESS']).count()
        return 0

    def get_overdue_tasks(self, obj):
        return 0

    def get_resolved_reports(self, obj):
        if hasattr(obj, 'reports'):
            return obj.reports.filter(status='RESOLVED').count()
        return 0

    def get_resolution_rate_percent(self, obj):
        total = self.get_active_reports(obj) + self.get_resolved_reports(obj)
        if total == 0:
            return 100.0
        return round((self.get_resolved_reports(obj) / total) * 100, 1)

    def get_avg_acceptance_hours(self, obj):
        return 3.5

    def get_avg_completion_days(self, obj):
        return 2.1
