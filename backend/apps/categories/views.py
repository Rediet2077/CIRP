from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from utils.responses import api_response
from .models import Category
from .serializers import CategorySerializer


class CategoryListView(generics.ListAPIView):
    """
    List infrastructure problem categories.
    GET /api/v1/categories/ and GET /categories
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.filter(is_active=True).select_related('default_department').order_by('name')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'code', 'description']
    filterset_fields = ['default_department']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            data=serializer.data,
            message="Categories retrieved successfully.",
            request=request
        )


class CategoryDetailView(generics.RetrieveAPIView):
    """
    Retrieve details for a specific infrastructure problem category.
    GET /api/v1/categories/<uuid>/
    """
    permission_classes = [AllowAny]
    queryset = Category.objects.all().select_related('default_department')
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            data=serializer.data,
            message="Category retrieved successfully.",
            request=request
        )
