from django.urls import path

from .registry_views import RegistryActivateView, RegistryHeartbeatView, RegistryValidateView

app_name = "license_registry"

urlpatterns = [
    path("activate/", RegistryActivateView.as_view(), name="registry-activate"),
    path("heartbeat/", RegistryHeartbeatView.as_view(), name="registry-heartbeat"),
    path("validate/", RegistryValidateView.as_view(), name="registry-validate"),
]
