from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vendors/", include("vendors.urls")),
    path("procurement/", include("procurement.urls")),
    path("contracts/", include("contracts.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit/", include("audit.urls")),
    path("reports/", include("dashboard.urls")),
    path("", include("it_assets.urls")),
]