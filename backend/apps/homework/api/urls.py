from rest_framework.routers import DefaultRouter

from .views import HomeworkViewSet

router = DefaultRouter(trailing_slash=False)
router.register("homework", HomeworkViewSet, basename="homework")

urlpatterns = router.urls
