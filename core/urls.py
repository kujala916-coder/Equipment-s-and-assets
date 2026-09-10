from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(template_name="it_assets/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("vendors/", include("vendors.urls")),
    path("procurement/", include("procurement.urls")),
    path("contracts/", include("contracts.urls")),
    path("notifications/", include("notifications.urls")),
    path("audit/", include("audit.urls")),
    path("reports/", include("dashboard.urls")),
    path("", include("it_assets.urls")),
]