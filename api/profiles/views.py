from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Follow, Notification
from .serializers import  ProfileSerializer, UserProfileSerializer
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import Follow
from yoga_sessions.views import SessionListCreateAPIView, SessionDetailAPIView,UserJoinedSessionsAPIView

User = get_user_model()

class FollowView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, username):
        """Follow a user"""
        try:
            user = request.user
            try:
                user_to_follow = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user == user_to_follow:
                return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the follow relationship already exists
            follow, created = Follow.objects.get_or_create(follower=user, following=user_to_follow)
            if created:
                Notification.objects.create(
                    recipient=user_to_follow,
                    actor=user,
                    verb='followed',
                    target='your profile'
                )
                user_dashboard = DashboardView()
                data = user_dashboard.get(request).data
                profile_view = ProfileView()
                profile_view.kwargs = {"username": username}  # Manually set kwargs

                profile_data = profile_view.get(request).data
                return Response({"message": f"You are now following {username}","user":data,'followUser' : profile_data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Already following this user"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
                return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        """Unfollow a user"""
        try:
            user = request.user
            try:
                user_to_unfollow = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            follow = Follow.objects.filter(follower=user, following=user_to_unfollow)
            if follow.exists():
                follow.delete()
                user_dashboard = DashboardView()
                data = user_dashboard.get(request).data
                profile_view = ProfileView()
                profile_view.kwargs = {"username": username}  # Manually set kwargs
                profile_data = profile_view.get(request).data
                return Response({"message": f"You have unfollowed {username}","user":data,'followUser' : profile_data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
                return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class FollowerListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer  # Assuming UserSerializer includes 'username'

    def get_queryset(self):
        try:
            username = self.kwargs.get("username")
            
            if not username:
                return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return User.objects.none()

            return user.followers.all().select_related('follower')  # Fetch the related 'follower' User instances
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class FollowingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer  # Assuming UserSerializer includes 'username'

    def get_queryset(self):
        try:
            username = self.kwargs.get("username")
            
            if not username:
                return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return User.objects.none()

            # Returning following (from the 'Follow' model), using select_related to fetch the related 'following' (User) instance
            return user.following.all().select_related('following')  # Fetch the related 'following' User instances
        except Exception:
                return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    """View to get authenticated user details along with followers and following."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user  # Get the logged-in user
            
           
            followers = user.followers.all().select_related('follower')  # Get all followers
            following = user.following.all().select_related('following')  # Get all following
            joined_sessions = UserJoinedSessionsAPIView().get(request).data
            notifications = user.notifications.all()  # Get all notifications for the user
            data = {
                "bio": user.bio,
                "is_trainer": user.is_trainer,
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "followers": [(follow.follower.username) for follow in followers],
                "following": [(follow.following.username) for follow in following],
                "date_joined": user.date_joined,
                "avatar" : request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                "notifications": [
                    {
                        "actor": notification.actor.username,
                        "verb": notification.verb,
                        "target": notification.target,
                        "timestamp": notification.timestamp
                    } for notification in notifications
                ],
                'joined_sessions': joined_sessions
            }
            if user.is_trainer:
                sessions = SessionListCreateAPIView()
                sessions = sessions.get(request).data
                data['sessions'] = sessions
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
                return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """View to get authenticated user details along with followers and following."""
    permission_classes = []

    def get(self, request):
        try:
            username = self.kwargs.get("username")
            user = User.objects.get(username=username)  # Get the logged-in user
            followers = user.followers.all().select_related('follower')  # Get all followers
            following = user.following.all().select_related('following')  # Get all following
            data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "followers": [(follow.follower.username) for follow in followers],
                "following": [(follow.following.username) for follow in following],
                "avatar" : request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                "date_joined": user.date_joined,
                "bio": user.bio,
                "is_trainer": user.is_trainer,
                }
            if user.is_trainer:
                sessions = SessionDetailAPIView()
                sessions = sessions.get(request,user.id).data
                data['sessions'] = sessions
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)


class AllUsersView(APIView):
    """View to get all users with followers and following details."""
    permission_classes = []

    def get(self, request):
        try:
            users = User.objects.all()
            data = []

            for user in users:
                followers = user.followers.all().select_related('follower')  # Get all followers
                following = user.following.all().select_related('following')  # Get all following
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "followers_count": followers.count(),
                    "following_count": following.count(),
                    "followers": [follow.follower.username for follow in followers],  # List of followers' usernames
                    "following": [follow.following.username for follow in following],  # List of following usernames
                    "date_joined": user.date_joined,
                    "avatar" : request.build_absolute_uri(user.avatar.url) if user.avatar else None,
                    "bio": user.bio,
                    "is_trainer": user.is_trainer,
                    }
                if user.is_trainer:
                    sessions = SessionDetailAPIView()
                    sessions = sessions.get(request,user.id).data
                    user_data['sessions'] = sessions
                data.append(user_data)

            return Response({"users": data}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "An unexpected error occured, try refreshing the page."}, status=status.HTTP_400_BAD_REQUEST)