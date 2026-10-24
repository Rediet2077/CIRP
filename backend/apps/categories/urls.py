from django.urls import re_path
from .views import CategoryListView, CategoryDetailView

urlpatterns = [
    re_path(r'^(?P<id>[0-9a-f-]+)/?$', CategoryDetailView.as_view(), name='category_detail'),
    re_path(r'^/?$', CategoryListView.as_view(), name='category_list'),
]
