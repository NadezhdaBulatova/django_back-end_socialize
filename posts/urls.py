from django.urls import path, include
from rest_framework import routers
from posts.views import PostViewSet

router = routers.DefaultRouter()
router.register("", PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
    path('by_author/<int:user_id>/', PostViewSet.as_view({'get': 'by_author'}), name='posts-by-author'),

]