from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from uuid import uuid4
from django.core.cache import cache

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['GET'])
def getRoutes(request):
    routes = [
        '/api/token',
        'api/token/refresh'
    ]
    return Response(routes)

class RegisterFilterApiView(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    def get(self, request, *args, **kwargs):
        ticket_uuid = str(uuid4()) #generate the random number with the guarantee to secure privacy
        if request.user.is_anonymous:
            cache.set(ticket_uuid, False)
        else: 
            if request.META.get('HTTP_TICKET_HEADER'):
                cache.set(ticket_uuid, {'user': request.user.id, 'socket_for': request.META.get('HTTP_TICKET_HEADER')})
        return Response({'ticket_uuid': ticket_uuid})