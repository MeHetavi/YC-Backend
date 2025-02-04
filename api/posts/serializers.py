from rest_framework import serializers
from .models import Post, Like, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username instead of user ID
    # likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'created_at', 'updated_at', 'comments_count']

class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    # post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    user = serializers.StringRelatedField(read_only=True)  # Display username instead of user ID

    class Meta:
        model = Like
        fields = ['user','post', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    # post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())
    user = serializers.StringRelatedField(read_only=True)  # Display username instead of user ID

    class Meta:
        model = Comment
        fields = ['id','post','user' ,'text', 'created_at']