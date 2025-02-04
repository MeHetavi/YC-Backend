from django.db import models

# Create your models here.
import uuid
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Unique UUID
    is_trainer = models.BooleanField(default=False)  # Differentiates trainers from trainees
    bio = models.TextField(blank=True, null=True)  # User biography
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)  # Profile picture

    def __str__(self):
        return self.username  # Displays username in admin panel