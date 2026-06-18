from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.accounts.api.urls")),
    path("api/", include("apps.patients.api.urls")),
    path("api/", include("apps.scheduling.api.urls")),
    path("api/", include("apps.mood.api.urls")),
    path("api/", include("apps.clinical.api.urls")),
]
