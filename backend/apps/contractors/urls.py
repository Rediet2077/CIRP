from django.urls import path
from .views import ContractorListCreateView, ContractorDetailView, ContractorTasksView

urlpatterns = [
    path('<str:pk>/tasks/', ContractorTasksView.as_view(), name='contractor_tasks'),
    path('<str:pk>/tasks', ContractorTasksView.as_view(), name='contractor_tasks_no_slash'),
    path('<str:pk>/', ContractorDetailView.as_view(), name='contractor_detail'),
    path('<str:pk>', ContractorDetailView.as_view(), name='contractor_detail_no_slash'),
    path('', ContractorListCreateView.as_view(), name='contractors_list_create'),
]
