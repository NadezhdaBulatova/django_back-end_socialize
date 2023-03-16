from rest_framework import serializers
from chat.models import Conversation, Message
from account.models import UserProfile

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'name', 'participants']

class MessageSerializer(serializers.ModelSerializer):
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())
    from_user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'from_user', 'content', 'timestamp']