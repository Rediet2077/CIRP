from django.urls import re_path
from .views import AssetListCreateView, AssetDetailView, AssetTypeListView

urlpatterns = [
    # Asset types: /api/v1/asset-types/ and /asset-types
    re_path(r'^asset-types/?$', AssetTypeListView.as_view(), name='asset_types_list'),

    # Assets: /api/v1/assets/ and /assets
    re_path(r'^assets/(?P<id>[0-9a-f-]+)/?$', AssetDetailView.as_view(), name='asset_detail'),
    re_path(r'^assets/?$', AssetListCreateView.as_view(), name='asset_list_create'),
]
