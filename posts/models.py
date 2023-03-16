from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from account.models import UserProfile

User=get_user_model()

class Post(models.Model):
    author = models.ForeignKey(to=UserProfile, on_delete=models.CASCADE, related_name="posts")
    text_content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='posts_pics', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
