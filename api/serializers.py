from .models import Card, User, FollowRelationship, CardStyleDeclaration
from rest_framework import serializers
from django.db import IntegrityError


class CardStyleBulkCreateUpdateSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        styles = [CardStyleDeclaration(**item) for item in validated_data]
        try:
            return CardStyleDeclaration.objects.bulk_create(styles)
        except IntegrityError as e:
            raise serializers.ValidationError({"error": str(e)})

    def update(self, instance, validated_data):
        properties = [obj["property"] for obj in self.validated_data]
        instances = CardStyleDeclaration.objects.filter(
            property__in=properties, card_id=instance.id
        )
        for style in self.validated_data:
            serializer = CardStyleDeclarationSerializer(data=style)
            serializer.is_valid(raise_exception=True)
            if instances.filter(property=style["property"]):
                styleInstance = instances.get(property=style["property"])
                if "boolValue" in style:
                    styleInstance.boolValue = style["boolValue"]
                elif "value" in style:
                    styleInstance.value = style["value"]
                try:
                    styleInstance.save()
                except IntegrityError as e:
                    raise serializers.ValidationError({"error": str(e)})

        return instances

    def validate(self, data):
        properties = [obj["property"] for obj in data if "property" in obj]
        if len(properties) != len(data):
            raise serializers.ValidationError(
                "All objects must have the 'property' key."
            )
        return data


class CardStyleDeclarationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardStyleDeclaration
        fields = ("property", "value", "boolValue")
        list_serializer_class = CardStyleBulkCreateUpdateSerializer


class CardSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="creator.username")
    styles = CardStyleDeclarationSerializer(many=True, read_only=True)
    creator_id = serializers.ReadOnlyField(source="creator.id")

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = [
            "id",
            "creator",
            "creator_id",
            "created_at",
            "updated_at",
            "styles",
        ]


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
