from rest_framework import serializers
from apps.departments.serializers import DepartmentRefSerializer
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for infrastructure problem categories.
    Compatible with Flutter's 3-column category grid and AI classification routing.
    """
    default_department = DepartmentRefSerializer(read_only=True)
    department_id = serializers.UUIDField(source='default_department_id', read_only=True)
    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'code',
            'description',
            'icon',
            'default_department',
            'department_id',
            'subcategories_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_subcategories_count(self, obj):
        return obj.subcategories.count() if hasattr(obj, 'subcategories') else 0
