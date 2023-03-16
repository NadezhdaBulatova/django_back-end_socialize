from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from account.api.serializers import UserProfileSerializer, UserAccountSerializer, UserProfileWithUserInfoSerializer
from account.models import UserAccount, UserProfile
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class ProfileViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfileWithUserInfoSerializer
        return UserProfileSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False)
    def all_except_user(self, request):
        profiles = self.queryset.exclude(user=request.user)
        page=self.paginate_queryset(profiles)
        serializer = UserProfileWithUserInfoSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def search(self, request):
        query = request.query_params.get('name', '')
        profiles = self.queryset.filter(
            Q(user__username__icontains=query) |
            Q(name__icontains=query) |
            Q(last_name__icontains=query)
        )
        page=self.paginate_queryset(profiles)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class RegisterUserAccountView(generics.CreateAPIView):
    queryset = UserAccount.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = UserAccountSerializer
    authentication_classes = ()

