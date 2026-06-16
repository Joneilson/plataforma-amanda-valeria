from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AdminDashboardView, AppointmentViewSet, PatientDashboardView

router = DefaultRouter(trailing_slash=False)
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = router.urls + [
    path("dashboard/admin", AdminDashboardView.as_view(), name="dashboard-admin"),
    path("dashboard/patient", PatientDashboardView.as_view(), name="dashboard-patient"),
]
