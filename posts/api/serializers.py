from rest_framework import serializers
from posts.models import Post
from account.models import UserProfile

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.id')
    image=serializers.ImageField(required=False)
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'text_content', "image", 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(author=UserProfile.objects.get(user=self.request.user))

