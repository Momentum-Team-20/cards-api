from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Card(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    front_text = models.CharField(max_length=255)
    back_text = models.CharField(max_length=255, null=True, blank=True)
    background_color = models.CharField(max_length=255)
    font = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
      return f"Card: {self.front_text}"


class Follow(models.Model):
    user_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follows_as_follower")
    user_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follows_as_followed_user")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_from.username} follows {self.user_to.username}"
