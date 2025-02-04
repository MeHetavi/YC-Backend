# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from profiles.views import DashboardView

User = get_user_model()

class UpdateUserView(APIView):
    """View to update user details."""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = request.user
            data = request.data
            serializer = UserSerializer(user, data=data, partial=True)  # Allows partial updates
            if serializer.is_valid():
                serializer.save()
                user_dashboard = DashboardView()
                data = user_dashboard.get(request).data
                return Response({"message": "User updated successfully","user":data}, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
            
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error':'An unexpected error occured.'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterUser(APIView):
    permission_classes = []

    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                return Response({
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error':'An unexpected error occured.'})
class LoginUser(APIView):
    permission_classes = []

    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error':f'An {Exception} occured.'})
