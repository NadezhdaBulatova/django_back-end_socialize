from chat.views import ConversationViewSet, MessageViewSet
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'conversations', ConversationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('messages/by_conversation/', MessageViewSet.as_view({'get': 'by_conversation'}), name='messages_by_conversation')
]