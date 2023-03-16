import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from urllib.parse import parse_qsl
from django.core.cache import cache
from chat.models import Conversation, Message
from datetime import datetime
from django.contrib.auth import get_user_model
from chat.api.serializers import MessageSerializer, ConversationSerializer
from uuid import UUID
from account.models import UserProfile
from account.api.serializers import UserProfileSimplifiedSerializer


class UUIDEncoder(json.JSONEncoder):
    def defautl(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conv_name = None
        self.conversation = None
        self.conv_participants = None
        self.conv_participants_list = None

    def connect(self):
        try:
            query_string = self.scope['query_string'].decode('utf-8')
            query_params = dict(parse_qsl(query_string))
            ticket_uuid = query_params.get('ticket_uuid')
            self.scope['has_ticket'] = cache.get(ticket_uuid)
            if self.scope['has_ticket']:
                self.user =  UserProfile.objects.get(user_id=self.scope['has_ticket']['user']) 
            if not cache.delete(ticket_uuid):
                raise Exception('Ticket not found')
        except:
            print('Error happened in chat consumer')
            self.close()
        self.conv_name = query_params.get('conv_name')
        self.conv_participants_list = self.conv_name.split('.')
        self.conversation, created = Conversation.objects.get_or_create(name=self.conv_name)
        if (created):
            self.conv_participants = UserProfile.objects.filter(user__username__in=self.conv_participants_list)
            self.conversation.participants.add(*self.conv_participants)
        async_to_sync(self.channel_layer.group_add)(self.conv_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)

    def receive_json(self, content, **kwargs):
        message_type = content["type"]
        if message_type == 'form_message':
            message=Message.objects.create(from_user=self.user, 
                                            content=content['message'],
                                            conversation=self.conversation)
            message.save()
            async_to_sync(self.channel_layer.group_send)(self.conv_name, {
                "type": "form_message_echo",
                "name": UserProfileSimplifiedSerializer(self.user).data,
                "message": MessageSerializer(message).data,
            })
        return super().receive_json(content, **kwargs)
    
    def form_message_echo(self, event):
        self.send_json(event)
    
    @classmethod
    def encode_json(cls, content):
        return json.dumps(content, cls=UUIDEncoder)
    

    