
from account.models import UserProfile
from django.db import models

class Conversation(models.Model):
    name = models.CharField(max_length=128)
    participants = models.ManyToManyField(to=UserProfile, blank=True, related_name='chat_participants')
    
    class Meta:
        verbose_name_plural = 'Conversations'


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    from_user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="messages_from_me"
    )
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']
