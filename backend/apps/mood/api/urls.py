from rest_framework.routers import DefaultRouter

from .views import MoodViewSet

router = DefaultRouter(trailing_slash=False)
router.register("mood", MoodViewSet, basename="mood")

urlpatterns = router.urls
