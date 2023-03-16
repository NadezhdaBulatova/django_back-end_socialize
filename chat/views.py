from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from chat.api.serializers import MessageSerializer, ConversationSerializer
from chat.models import Message, Conversation
from rest_framework import viewsets 
from rest_framework.decorators import action
from rest_framework.parsers import  FormParser, JSONParser
from rest_framework import status

class ConversationViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    parser_classes = (JSONParser, FormParser)
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

class MessageViewSet(viewsets.ModelViewSet):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    parser_classes = (JSONParser, FormParser)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        conversation_name = request.query_params.get('conversation_name')
        if not conversation_name:
            return Response({'error': 'conversation_name is required'}, status=400)
        queryset = self.get_queryset().filter(conversation__name=conversation_name)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
