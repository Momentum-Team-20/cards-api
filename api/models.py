from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    followed_users = models.ManyToManyField(
        "self",
        through="FollowRelationship",
        related_name="followed_by",
        symmetrical=False,
    )

    def follow_another_user(self, other_user):
        relationship, created = FollowRelationship.objects.get_or_create(
            follower=self, followed_user=other_user
        )
        return relationship

    def unfollow_another_user(self, other_user):
        FollowRelationship.objects.filter(
            follower=self, followed_user=other_user
        ).delete()

    def block_follower(self, other_user):
        relationship = FollowRelationship.objects.get(
            follower=other_user, followed_user=self
        )
        relationship.status = FollowRelationship.Status.BLOCKED
        relationship.save()
        return relationship

    def unblock_follower(self, other_user):
        relationship = FollowRelationship.objects.get(
            follower=other_user, followed_user=self
        )
        relationship.status = FollowRelationship.Status.ACTIVE
        relationship.save()
        return relationship

    def get_relationships_where_follower(self):
        return self.ACTIVE.filter(status=FollowRelationship.Status.ACTIVE)

    def get_relationships_where_followed(self):
        return self.followers.filter(status=FollowRelationship.Status.ACTIVE)

    def get_users_blocking_me(self):
        return self.ACTIVE.filter(status=FollowRelationship.Status.BLOCKED)

    def get_blocked_followers(self):
        return self.followers.filter(status=FollowRelationship.Status.BLOCKED)


class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Card(BaseModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cards")
    front_text = models.CharField(max_length=255)
    back_text = models.CharField(max_length=255, null=True, blank=True)
    imageURL = models.URLField(max_length=200, null=True, blank=True)
    background_color = models.CharField(max_length=255, null=True, blank=True)
    font = models.CharField(max_length=255, null=True, blank=True)
    font_size = models.CharField(max_length=255, null=True, blank=True)
    text_align = models.CharField(max_length=255, null=True, blank=True)
    draft = models.BooleanField(
        default=False
    )  # false because front end may not implement draft feature

    def __str__(self):
        return f"Card: {self.front_text}"


class CardStyleDeclaration(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="styles")
    property = models.CharField(max_length=255)
    value = models.CharField(max_length=255, null=True, blank=True)
    boolValue = models.BooleanField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["property", "card"], name="no duplicate properties per card"
            ),
            models.CheckConstraint(
                check=(
                    models.Q(value__isnull=False) & models.Q(boolValue__isnull=True)
                    | models.Q(boolValue__isnull=False) & models.Q(value__isnull=True)
                ),
                name="one_of_two_fields_null_constraint",
            ),
        ]

    def __str__(self):
        return f"Card {self.card.pk} style - {self.property}: {self.value}"


class FollowRelationship(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = (1, "Active")
        BLOCKED = (0, "Blocked")

    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="relationship_as_follower"
    )
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="relationship_as_followed_user"
    )
    status = models.IntegerField(choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.followed_user.username}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "followed_user"], name="unique_follows"
            )
        ]
