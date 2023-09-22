from .models import Card, User, FollowRelationship, CardStyleDeclaration
from rest_framework import serializers


class CardStyleBulkCreateUpdateSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        styles = [CardStyleDeclaration(**item) for item in validated_data]

        return CardStyleDeclaration.objects.bulk_create(styles, ignore_conflicts=True)

    def update(self, instance, validated_data):
        properties = [obj["property"] for obj in self.validated_data]
        instances = CardStyleDeclaration.objects.filter(
            property__in=properties, card_id=instance.id
        )
        for style in self.validated_data:
            instance = instances.get(property=style["property"])
            instance.value = style["value"]
            instance.save()
        return instances


class CardStyleDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardStyleDeclaration
        fields = ("property", "value")
        list_serializer_class = CardStyleBulkCreateUpdateSerializer


class CardSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="creator.username")
    styles = CardStyleDeclarationSerializer(many=True, read_only=True)

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "creator", "styles"]


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
