from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import models
from users.models import CustomUser
User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):    
    class Meta:
        model = models.Follow
        fields = "__all__"

class UserProfileSerializer(serializers.ModelSerializer):    
    class Meta:
        model = CustomUser
        fields = [ 'username', 'email', 'password','first_name','last_name','is_trainer']