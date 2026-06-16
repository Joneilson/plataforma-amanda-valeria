from rest_framework.routers import DefaultRouter

from .views import PatientViewSet

router = DefaultRouter(trailing_slash=False)
router.register("patients", PatientViewSet, basename="patient")

urlpatterns = router.urls
