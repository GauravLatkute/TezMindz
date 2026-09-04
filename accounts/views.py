from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.models import User
from accounts.serializers import RegisterSerializer, UserSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "message": "Student account created successfully",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        }
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed during registration",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password",
                    "errors": {"detail": str(e)}
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = User.objects.get(username=request.data.get("username"))
        user_data = UserSerializer(user).data

        return Response(
            {
                "success": True,
                "message": "Login successful",
                "data": {
                    "refresh": serializer.validated_data["refresh"],
                    "access": serializer.validated_data["access"],
                    "user": user_data
                }
            },
            status=status.HTTP_200_OK
        )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "Token refresh failed or token is invalid",
                    "errors": {"detail": str(e)}
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {
                "success": True,
                "message": "Token refreshed successfully",
                "data": serializer.validated_data
            },
            status=status.HTTP_200_OK
        )


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "success": True,
            "message": "Profile retrieved successfully",
            "data": serializer.data
        })

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        return Response(
            {
                "success": False,
                "message": "Validation failed during profile update",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
