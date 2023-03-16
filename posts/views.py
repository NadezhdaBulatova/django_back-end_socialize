from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from posts.api.serializers import PostSerializer
from posts.models import Post
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from account.models import UserProfile

class PostViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    parser_classes = (JSONParser, FormParser, MultiPartParser)
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=UserProfile.objects.get(user=self.request.user))

 
    @action(detail=False, methods=['get'])
    def by_author(self, request, user_id=None):
        if user_id is not None:
            posts = self.queryset.filter(author__user__id=user_id)
            page=self.paginate_queryset(posts)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else: 
            return super().retrieve(request)
