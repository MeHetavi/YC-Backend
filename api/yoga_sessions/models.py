import datetime
import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trainer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vc_urls")
    url = models.URLField()
    title = models.CharField(max_length=500)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, max_length=10000)
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=1000.00)
    duration = models.IntegerField(default=30)
    accept_participants = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.trainer.name} - {self.title}"

class SessionParticipant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="joined_sessions")
    joined_at = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()
    class Meta:
        unique_together = ('session', 'user')  # Prevents duplicate entries for the same session-user pair

    def __str__(self):
        return f"{self.user.username} joined {self.session.title}"
