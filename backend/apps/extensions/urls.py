from django.urls import path
from .views import ExtensionListCreateView, DecideExtensionView

urlpatterns = [
    path('<str:pk>/decide/', DecideExtensionView.as_view(), name='decide_extension'),
    path('<str:pk>/decide', DecideExtensionView.as_view(), name='decide_extension_no_slash'),
    path('', ExtensionListCreateView.as_view(), name='extensions_list_create'),
]
