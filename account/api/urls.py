from django.urls import path
from account.api.views import getRoutes, MyTokenObtainPairView, RegisterFilterApiView

from rest_framework_simplejwt.views import (
    TokenRefreshView
)

urlpatterns = [
    path('', getRoutes),
    path('ticket', RegisterFilterApiView.as_view()),
    path('token', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]