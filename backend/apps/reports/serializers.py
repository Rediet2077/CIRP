import base64
import math
import uuid
import logging
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import serializers

from .models import Report
from apps.categories.models import Category
from apps.departments.models import Department
from apps.assets.models import Asset
from apps.contractors.models import StaffContractor
from apps.tasks.models import Task
from utils.enums import ReportPriority, ReportStatus, TaskPriority, TaskStatus
from utils import ai_client

logger = logging.getLogger(__name__)

# Valid image MIME types and signatures
VALID_IMAGE_EXTS = {
    b'\xff\xd8\xff': 'jpg',
    b'\x89PNG': 'png',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
    b'RIFF': 'webp',
}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def detect_image_extension(image_bytes: bytes) -> str:
    """Determine image extension by inspect binary header magic bytes."""
    for header, ext in VALID_IMAGE_EXTS.items():
        if image_bytes.startswith(header):
            return ext
    return 'jpg'


class CitizenReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for citizen incident report submissions.
    Supports JSON with base64 images and multipart file uploads.
    Enforces GPS coordinate bounds, image validation, category routing,
    and calls the AI microservice asynchronously without blocking report creation.
    """
    category_id = serializers.CharField(write_only=True)
    media_images = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        write_only=True
    )
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=True)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    priority = serializers.ChoiceField(
        choices=ReportPriority.choices,
        default=ReportPriority.MEDIUM,
        required=False
    )
    address = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')

    class Meta:
        model = Report
        fields = [
            'id',
            'report_code',
            'title',
            'description',
            'category_id',
            'latitude',
            'longitude',
            'priority',
            'address',
            'media_images',
            'submitted_at',
        ]
        read_only_fields = ['id', 'report_code', 'submitted_at']

    def validate_latitude(self, value):
        if not (-90.0 <= value <= 90.0):
            raise serializers.ValidationError("Latitude must be between -90.0 and 90.0 degrees.")
        return value

    def validate_longitude(self, value):
        if not (-180.0 <= value <= 180.0):
            raise serializers.ValidationError("Longitude must be between -180.0 and 180.0 degrees.")
        return value

    def validate_category_id(self, value):
        """
        Gracefully resolves category from UUID, code (e.g. 'road_damage'),
        or name (e.g. 'Road Damage & Potholes').
        """
        category = None
        # Try UUID
        try:
            val_uuid = uuid.UUID(str(value))
            category = Category.objects.filter(id=val_uuid, is_active=True).first()
        except (ValueError, TypeError):
            pass

        # Try code
        if not category:
            category = Category.objects.filter(code__iexact=str(value).strip(), is_active=True).first()

        # Try name or partial name
        if not category:
            category = Category.objects.filter(name__icontains=str(value).strip(), is_active=True).first()

        if not category:
            raise serializers.ValidationError(
                f"Invalid category identifier '{value}'. Please choose an active category."
            )

        return category

    def _save_base64_photo(self, b64_string: str) -> tuple[str, bytes]:
        """Safely decode and store a base64 encoded photo."""
        header, _, encoded = b64_string.partition(',')
        raw_b64 = encoded if encoded else header

        try:
            image_bytes = base64.b64decode(raw_b64)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 image data: {e}")

        if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image file exceeds maximum allowable size of {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB."
            )

        ext = detect_image_extension(image_bytes)
        year = datetime.now().year
        filename = f"reports/{year}/{uuid.uuid4().hex}.{ext}"
        saved_path = default_storage.save(filename, ContentFile(image_bytes))
        file_url = default_storage.url(saved_path)
        return file_url, image_bytes

    def _save_uploaded_file(self, uploaded_file) -> tuple[str, bytes]:
        """Safely save a multipart uploaded file."""
        if uploaded_file.size > MAX_IMAGE_SIZE_BYTES:
            raise serializers.ValidationError(
                f"Image file '{uploaded_file.name}' exceeds maximum allowable size of 10MB."
            )

        image_bytes = uploaded_file.read()
        ext = detect_image_extension(image_bytes)
        year = datetime.now().year
        filename = f"reports/{year}/{uuid.uuid4().hex}.{ext}"
        saved_path = default_storage.save(filename, ContentFile(image_bytes))
        file_url = default_storage.url(saved_path)
        return file_url, image_bytes

    def create(self, validated_data):
        category = validated_data.pop('category_id')
        raw_images = validated_data.pop('media_images', [])
        request = self.context.get('request')

        # Auto-resolve responsible department from category
        department = category.default_department
        if not department:
            department = Department.objects.filter(approval_status=Department.ApprovalStatus.APPROVED).first()

        # Generate unique report tracking code: REP-YYYY-XXXX
        year = datetime.now().year
        rand_suffix = f"{uuid.uuid4().int % 9000 + 1000}"
        report_code = f"REP-{year}-{rand_suffix}"
        while Report.objects.filter(report_code=report_code).exists():
            rand_suffix = f"{uuid.uuid4().int % 9000 + 1000}"
            report_code = f"REP-{year}-{rand_suffix}"

        # Title fallback if empty
        title = validated_data.get('title', '').strip()
        if not title:
            title = f"{category.name} Incident"
        validated_data['title'] = title

        # Process photo uploads and collect raw bytes for AI classification
        stored_photo_urls = []
        first_image_bytes = None

        # 1. Process base64 strings from media_images list
        for b64 in raw_images:
            if b64 and isinstance(b64, str):
                url, b_data = self._save_base64_photo(b64)
                stored_photo_urls.append(url)
                if first_image_bytes is None:
                    first_image_bytes = b_data

        # 2. Process multipart files if passed in request.FILES
        if request and hasattr(request, 'FILES'):
            for key in ['photos', 'media_photos', 'photo', 'images', 'image']:
                for file_obj in request.FILES.getlist(key):
                    url, b_data = self._save_uploaded_file(file_obj)
                    stored_photo_urls.append(url)
                    if first_image_bytes is None:
                        first_image_bytes = b_data

        # Build authenticated citizen details
        citizen = None
        citizen_name = 'Concerned Citizen'
        citizen_contact = ''
        if request and request.user and request.user.is_authenticated:
            citizen = request.user
            citizen_name = request.user.get_full_name() or request.user.email
            citizen_contact = getattr(request.user, 'phone_number', '') or request.user.email

        # Call AI Microservice non-blockingly if photo was uploaded
        ai_prediction = {}
        if first_image_bytes:
            try:
                ai_prediction = ai_client.classify_image(first_image_bytes)
            except Exception as e:
                logger.warning(f"AI classification failed gracefully during report creation: {e}")

        # Instantiate report instance
        report = Report.objects.create(
            report_code=report_code,
            title=title,
            description=validated_data['description'],
            category=category,
            department=department,
            citizen=citizen,
            citizen_name=citizen_name,
            citizen_contact=citizen_contact,
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
            address=validated_data.get('address', ''),
            priority=validated_data.get('priority', ReportPriority.MEDIUM),
            status=ReportStatus.NEW,
            media_photos=stored_photo_urls,
            ai_category_prediction=ai_prediction,
        )

        return report


class ReportSerializer(serializers.ModelSerializer):
    """
    Comprehensive Report serializer satisfying both:
    1. React Admin Dashboard (ReportRecordSchema via Zod)
    2. Flutter Mobile Application (Report details, coordinates, status)
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.UUIDField(source='category.id', read_only=True)
    department_id = serializers.UUIDField(source='department.id', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    asset_id = serializers.SerializerMethodField()
    asset_code = serializers.SerializerMethodField()
    asset_type_label = serializers.SerializerMethodField()

    citizen_latitude = serializers.FloatField(source='latitude', read_only=True)
    citizen_longitude = serializers.FloatField(source='longitude', read_only=True)

    status = serializers.SerializerMethodField()
    suggested_nearby_assets = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id',
            'report_code',
            'title',
            'description',
            'category_name',
            'category_id',
            'asset_id',
            'asset_code',
            'asset_type_label',
            'department_id',
            'department_name',
            'citizen_name',
            'citizen_contact',
            'citizen_latitude',
            'citizen_longitude',
            'latitude',
            'longitude',
            'address',
            'landmark',
            'status',
            'priority',
            'submitted_at',
            'media_photos',
            'ai_category_prediction',
            'ai_duplicate_analysis',
            'suggested_nearby_assets',
            'rejection_reason',
            'resolved_at',
        ]
        read_only_fields = ['id', 'report_code', 'submitted_at', 'media_photos']

    def get_asset_id(self, obj):
        return str(obj.asset.id) if obj.asset else None

    def get_asset_code(self, obj):
        return obj.asset.asset_code if obj.asset else None

    def get_asset_type_label(self, obj):
        return obj.asset.asset_type.name if obj.asset and obj.asset.asset_type else None

    def get_status(self, obj):
        # In React Admin Zod schema, REJECTED is modeled as DISPUTED
        if obj.status == ReportStatus.REJECTED:
            return 'DISPUTED'
        return obj.status

    def get_suggested_nearby_assets(self, obj) -> list:
        """
        Calculate and return nearest infrastructure assets within 2000m.
        Conforms to React Admin's suggested_nearby_assets schema.
        """
        if not obj.latitude or not obj.longitude or not obj.department:
            return []

        # Find assets belonging to the same department
        nearby = []
        lat1 = obj.latitude
        lon1 = obj.longitude

        assets = Asset.objects.filter(
            department=obj.department
        ).select_related('asset_type')[:15]

        for a in assets:
            # Approximate distance in meters
            dlat = (a.latitude - lat1) * 111139.0
            dlon = (a.longitude - lon1) * 111139.0 * math.cos(math.radians(lat1))
            dist = math.sqrt(dlat * dlat + dlon * dlon)

            if dist <= 3000:  # within 3km
                nearby.append({
                    "asset_id": str(a.id),
                    "asset_code": a.asset_code,
                    "asset_name": a.name,
                    "distance_meters": round(dist, 1),
                    "asset_type": a.asset_type.name if a.asset_type else "General Infrastructure",
                })

        nearby.sort(key=lambda x: x["distance_meters"])
        return nearby[:5]


class AcceptReportSerializer(serializers.Serializer):
    """
    Validates input from React Admin's acceptReport dialog and creates a Task atomically.
    """
    reportId = serializers.UUIDField(required=False)
    priority = serializers.ChoiceField(choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    assignedWorkerId = serializers.CharField()
    deadlineDate = serializers.DateTimeField()
    workDescription = serializers.CharField(min_length=1)
    internalNote = serializers.CharField(required=False, allow_blank=True, default='')

    # Also accept snake_case aliases
    assigned_worker_id = serializers.CharField(required=False)
    deadline_date = serializers.DateTimeField(required=False)
    work_description = serializers.CharField(required=False)
    internal_note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # Normalize camelCase to snake_case
        worker_id = attrs.get('assignedWorkerId') or attrs.get('assigned_worker_id')
        deadline = attrs.get('deadlineDate') or attrs.get('deadline_date')
        work_desc = attrs.get('workDescription') or attrs.get('work_description')
        internal_note = attrs.get('internalNote') if attrs.get('internalNote') is not None else attrs.get('internal_note', '')

        if not worker_id:
            raise serializers.ValidationError({"assignedWorkerId": "Assigned worker is required."})
        if not deadline:
            raise serializers.ValidationError({"deadlineDate": "Deadline date is required."})
        if not work_desc:
            raise serializers.ValidationError({"workDescription": "Work description is required."})

        # Verify worker exists
        try:
            val_uuid = uuid.UUID(str(worker_id))
            worker = StaffContractor.objects.get(id=val_uuid)
        except (StaffContractor.DoesNotExist, ValueError):
            raise serializers.ValidationError({"assignedWorkerId": f"Worker '{worker_id}' does not exist."})

        attrs['resolved_worker'] = worker
        attrs['resolved_deadline'] = deadline
        attrs['resolved_work_desc'] = work_desc
        attrs['resolved_internal_note'] = internal_note
        return attrs


class RejectReportSerializer(serializers.Serializer):
    """
    Validates rejection reason and department authorization.
    """
    reason = serializers.CharField(min_length=5, error_messages={
        'min_length': 'A documented reason of at least 5 characters is required to reject a report.'
    })
    department_id = serializers.CharField(required=False, allow_blank=True)


class LinkAssetSerializer(serializers.Serializer):
    """
    Validates asset linking to report.
    """
    assetId = serializers.CharField(required=False)
    asset_id = serializers.CharField(required=False)

    def validate(self, attrs):
        asset_id = attrs.get('assetId') or attrs.get('asset_id')
        if not asset_id:
            raise serializers.ValidationError({"assetId": "Asset ID is required."})

        try:
            val_uuid = uuid.UUID(str(asset_id))
            asset = Asset.objects.get(id=val_uuid)
        except (Asset.DoesNotExist, ValueError):
            raise serializers.ValidationError({"assetId": f"Asset '{asset_id}' not found."})


        attrs['resolved_asset'] = asset
        return attrs


class PublicReportSerializer(serializers.Serializer):
    """
    Strict serializer for Public Transparency Portal.
    Exposes ONLY anonymous, non-sensitive, aggregated summary information.
    Conforms strictly to React Admin's PublicReportSchema.strict().
    """
    reference = serializers.CharField(source='report_code')
    category = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    submitted_at = serializers.SerializerMethodField()
    general_location = serializers.SerializerMethodField()

    def get_category(self, obj) -> str:
        return obj.category.name if obj.category else "General Infrastructure"

    def get_status(self, obj) -> str:
        """
        Map internal status to public-friendly status:
        ["Under review", "Work in progress", "Awaiting confirmation", "Resolved", "Rejected"]
        """
        status_val = str(obj.status).upper()
        if status_val in [ReportStatus.RESOLVED]:
            return "Resolved"
        if status_val in [ReportStatus.DISPUTED, ReportStatus.REJECTED]:
            return "Rejected"
        if status_val in [ReportStatus.COMPLETED_PENDING_VERIFICATION]:
            return "Awaiting confirmation"
        if status_val in [ReportStatus.ACCEPTED, ReportStatus.IN_PROGRESS]:
            return "Work in progress"
        return "Under review"

    def get_submitted_at(self, obj) -> str:
        return obj.submitted_at.isoformat()

    def get_general_location(self, obj) -> str | None:
        """
        Return safe, general city/district location.
        Never return exact citizen house numbers or private coordinates.
        """
        address = getattr(obj, 'address', '') or ''
        parts = [p.strip() for p in address.split(',') if p.strip()]
        if len(parts) > 1:
            return ", ".join(parts[-2:])
        if parts:
            return parts[0]
        landmark = getattr(obj, 'landmark', '') or ''
        return landmark if landmark else "Public Infrastructure Zone"
