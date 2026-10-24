from rest_framework import serializers
from django.utils import timezone
from .models import Asset, AssetType
from apps.departments.models import Department
from utils.enums import AssetStatus, AssetCondition


class AssetTypeSerializer(serializers.ModelSerializer):
    """
    Asset Type definition matching React AssetTypeDefinitionSchema.
    """
    responsible_department_id = serializers.UUIDField(source='responsible_department.id', read_only=True)
    responsible_department_name = serializers.CharField(source='responsible_department.name', default='', read_only=True)
    category_id = serializers.SerializerMethodField()
    total_assets_count = serializers.SerializerMethodField()

    class Meta:
        model = AssetType
        fields = [
            'id',
            'name',
            'description',
            'category_id',
            'responsible_department_id',
            'responsible_department_name',
            'requires_location',
            'is_active',
            'total_assets_count',
        ]

    def get_category_id(self, obj):
        mapping = {
            'street_light': 'streetlight_failure',
            'road': 'road_damage',
            'water_point': 'water_leakage',
            'drainage': 'drainage',
            'waste_bin': 'garbage',
            'public_building': 'public_facility',
        }
        return mapping.get(obj.id, 'other')

    def get_total_assets_count(self, obj):
        return obj.assets.count() if hasattr(obj, 'assets') else 0


class AssetSerializer(serializers.ModelSerializer):
    """
    Full Asset record matching React AssetRecordSchema and Map components.
    """
    asset_type_id = serializers.CharField(source='asset_type.id', read_only=True)
    asset_type_label = serializers.CharField(source='asset_type.name', read_only=True)
    department_id = serializers.UUIDField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    registered_by = serializers.SerializerMethodField()
    registered_at = serializers.DateTimeField(source='created_at', read_only=True)
    active_reports_count = serializers.SerializerMethodField()
    installation_date = serializers.SerializerMethodField()
    last_inspection_date = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id',
            'asset_code',
            'asset_type_id',
            'asset_type_label',
            'department_id',
            'department_name',
            'name',
            'description',
            'status',
            'condition',
            'installation_date',
            'last_inspection_date',
            'latitude',
            'longitude',
            'address',
            'landmark',
            'registered_by',
            'registered_at',
            'updated_at',
            'active_reports_count',
            'specific_data',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_registered_by(self, obj):
        if obj.registered_by:
            full = f"{obj.registered_by.first_name} {obj.registered_by.last_name}".strip()
            return full if full else obj.registered_by.email
        return "Municipal GIS Core"

    def get_installation_date(self, obj):
        return str(obj.installation_date) if obj.installation_date else str(timezone.now().date())

    def get_last_inspection_date(self, obj):
        return str(obj.last_inspection_date) if obj.last_inspection_date else str(timezone.now().date())

    def get_active_reports_count(self, obj):
        if hasattr(obj, 'reports'):
            return obj.reports.filter(status__in=['NEW', 'ACCEPTED', 'IN_PROGRESS']).count()
        return 0


class AssetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for registering physical municipal assets from React Admin.
    Handles coordinate range validation and dynamic technical specifications.
    """
    asset_type = serializers.CharField(required=False)
    asset_type_id = serializers.CharField(required=False)
    department_id = serializers.UUIDField(required=True)
    latitude = serializers.FloatField(min_value=-90.0, max_value=90.0)
    longitude = serializers.FloatField(min_value=-180.0, max_value=180.0)

    class Meta:
        model = Asset
        fields = [
            'asset_code',
            'asset_type',
            'asset_type_id',
            'department_id',
            'name',
            'description',
            'status',
            'condition',
            'installation_date',
            'latitude',
            'longitude',
            'address',
            'landmark',
            'specific_data',
        ]

    def validate_asset_code(self, value):
        code = value.strip().upper()
        if Asset.objects.filter(asset_code=code).exists():
            raise serializers.ValidationError(f"Asset code '{code}' is already registered in the municipal inventory.")
        return code

    def validate(self, attrs):
        # Resolve asset_type identifier
        type_id = attrs.pop('asset_type', None) or attrs.pop('asset_type_id', None)
        if not type_id:
            raise serializers.ValidationError({"asset_type": "Asset type is required."})

        type_id = str(type_id).strip().lower()
        try:
            asset_type = AssetType.objects.get(id=type_id)
        except AssetType.DoesNotExist:
            raise serializers.ValidationError({"asset_type": f"Asset type '{type_id}' is not recognized."})

        attrs['asset_type'] = asset_type

        # Resolve department
        dept_id = attrs.pop('department_id')
        try:
            dept = Department.objects.get(id=dept_id)
        except Department.DoesNotExist:
            raise serializers.ValidationError({"department_id": "Department not found."})

        attrs['department'] = dept

        # Pack any additional fields into specific_data if passed at top level
        initial_data = self.initial_data
        specs = attrs.get('specific_data', {})
        if not specs:
            specs = {}

        for prefix in ['sl_', 'rd_', 'wp_', 'dr_', 'wb_', 'pb_']:
            for key, val in initial_data.items():
                if key.startswith(prefix) and key not in specs:
                    specs[key] = val

        attrs['specific_data'] = specs
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user if 'request' in self.context else None
        return Asset.objects.create(registered_by=user, **validated_data)
