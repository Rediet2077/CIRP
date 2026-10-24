from django.urls import re_path
from .views import DepartmentListView, DepartmentDetailView

urlpatterns = [
    re_path(r'^(?P<id>[0-9a-f-]+)/?$', DepartmentDetailView.as_view(), name='department_detail'),
    re_path(r'^/?$', DepartmentListView.as_view(), name='department_list'),
]
