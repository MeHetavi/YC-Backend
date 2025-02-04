from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model

User = get_user_model()

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # User who follows
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")  # User being followed
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Prevent duplicate follows

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    verb = models.CharField(max_length=255)  # e.g., 'followed', 'liked', 'commented'
    target = models.CharField(max_length=255, blank=True, null=True)  # e.g., 'post', 'profile', 'session'
    timestamp = models.DateTimeField(auto_now_add=True)
    # read = models.BooleanField(default=False)  # To mark notification as read or unread

    def __str__(self):
        return f"{self.actor.username} {self.verb} {self.target}"