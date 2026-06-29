from django.urls import path

from .views import ConversationListView, MessageListCreateView, MyConversationView

urlpatterns = [
    path("my-conversation", MyConversationView.as_view(), name="my-conversation"),
    path("conversations", ConversationListView.as_view(), name="conversation-list"),
    path("messages", MessageListCreateView.as_view(), name="message-list-create"),
]
