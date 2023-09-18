from .models import Card
from rest_framework import serializers


class CardSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source="creator.username")

    class Meta:
        model = Card
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "creator"]
