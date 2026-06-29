from django.urls import path

from .views import VideoRoomView

urlpatterns = [
    path("video/rooms/<int:appointment_id>", VideoRoomView.as_view()),
]
