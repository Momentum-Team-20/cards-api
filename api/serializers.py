from .models import Card, User, FollowRelationship
from rest_framework import serializers


class CardSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "creator"]


class FollowerUserSerializer(serializers.ModelSerializer):
    relationship_created = serializers.SlugRelatedField(
        slug_field="created_at", read_only=True
    )

    class Meta:
        model = User
        fields = ["id", "username", "relationship_created"]


class FollowRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowRelationship
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "follower",
        ]
