from django.shortcuts import render
from rest_framework import viewsets, permissions, response
from rest_framework.decorators import action
from .models import Card
from .serializers import CardSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all().order_by("created_at")
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(draft=False)

    @action(detail=False, methods=["get"])
    def me(self, request):
        cards = self.queryset.filter(creator=request.user)
        return response.Response(self.serializer_class(cards, many=True).data)
