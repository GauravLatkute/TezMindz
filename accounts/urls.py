from django.urls import path
from accounts.views import (
    RegisterView,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserProfileView
)

app_name = "accounts"

urlpatterns = [
    # Custom JWT authenticated API endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    
    # User profiles
    path("me/", UserProfileView.as_view(), name="me"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]
