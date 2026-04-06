from django.urls import path

from .views import FeatureCheckView, HeartbeatView, RegisterInstanceView, TicketForwardView, UsageReportView

app_name = "platform_gateway"

urlpatterns = [
    path("register-instance/", RegisterInstanceView.as_view(), name="gateway-register"),
    path("heartbeat/", HeartbeatView.as_view(), name="gateway-heartbeat"),
    path("usage-report/", UsageReportView.as_view(), name="gateway-usage-report"),
    path("feature-check/", FeatureCheckView.as_view(), name="gateway-feature-check"),
    path("ticket/", TicketForwardView.as_view(), name="gateway-ticket"),
]
