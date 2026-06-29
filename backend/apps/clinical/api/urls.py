from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ClinicalRecordViewSet, PatientNoteViewSet, SharedNoteListView

router = DefaultRouter(trailing_slash=False)
router.register("notes", PatientNoteViewSet, basename="note")
router.register("clinical-records", ClinicalRecordViewSet, basename="clinical-record")

urlpatterns = router.urls + [
    path("shared-notes", SharedNoteListView.as_view(), name="shared-notes"),
]
