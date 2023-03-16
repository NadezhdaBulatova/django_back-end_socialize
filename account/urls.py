from account.views import ProfileViewSet, RegisterUserAccountView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register('', ProfileViewSet, basename="profile")

urlpatterns = [
    path('register/', RegisterUserAccountView.as_view(), name="register"),
    path('', include(router.urls)), 
    path('all_except_user', ProfileViewSet.as_view({'get': 'all_except_user'}), name='all_except_user'),
    path('search', ProfileViewSet.as_view({'get': 'search'}), name='search_profiles'),
    path('api/', include('account.api.urls')),

]