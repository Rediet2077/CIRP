from rest_framework import generics, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from utils.responses import api_response, error_response
from utils.permissions import IsDepartmentAdmin, IsSystemAdmin
from .models import Asset, AssetType
from .serializers import AssetSerializer, AssetCreateSerializer, AssetTypeSerializer


class AssetTypeListView(generics.ListAPIView):
    """
    List physical municipal asset types.
    GET /api/v1/asset-types/ and GET /asset-types
    """
    permission_classes = [AllowAny]
    queryset = AssetType.objects.filter(is_active=True).select_related('responsible_department')
    serializer_class = AssetTypeSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Matches React AssetTypeListResponseSchema: z.array(AssetTypeDefinitionSchema)
        return api_response(
            data=serializer.data,
            message="Asset types retrieved successfully.",
            request=request
        )


class AssetListCreateView(generics.ListCreateAPIView):
    """
    Municipal physical asset registry.
    GET /api/v1/assets/ and GET /assets
    POST /api/v1/assets/ and POST /assets
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['asset_code', 'name', 'address', 'landmark']
    filterset_fields = ['department', 'asset_type', 'status', 'condition']
    ordering_fields = ['created_at', 'asset_code', 'condition']

    def get_queryset(self):
        qs = Asset.objects.all().select_related('asset_type', 'department', 'registered_by')
        dept_id = self.request.query_params.get('department_id')
        if dept_id and dept_id.lower() != 'all':
            qs = qs.filter(department_id=dept_id)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AssetCreateSerializer
        return AssetSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsDepartmentAdmin()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Matches React AssetListResponseSchema: z.array(AssetRecordSchema)
        return api_response(
            data=serializer.data,
            message="Assets retrieved successfully.",
            request=request
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return error_response(
                message="Asset registration failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
                request=request
            )

        asset = serializer.save()
        output_data = AssetSerializer(asset).data

        return api_response(
            data=output_data,
            message="Asset registered successfully.",
            status_code=status.HTTP_201_CREATED,
            request=request
        )


class AssetDetailView(generics.RetrieveUpdateAPIView):
    """
    Detailed physical asset view and specification inspection.
    GET /api/v1/assets/<uuid>/
    PATCH /api/v1/assets/<uuid>/
    """
    queryset = Asset.objects.all().select_related('asset_type', 'department', 'registered_by')
    serializer_class = AssetSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsDepartmentAdmin()]
        return [AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            data=serializer.data,
            message="Asset details retrieved successfully.",
            request=request
        )
