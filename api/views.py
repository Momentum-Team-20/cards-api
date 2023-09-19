from django.shortcuts import render
from rest_framework import viewsets, permissions, response
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from .models import Card, User, FollowRelationship
from .serializers import CardSerializer, FollowerUserSerializer
from .permissions import IsCreatorOrReadOnly


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all().order_by("created_at")
    serializer_class = CardSerializer
    permission_classes = [IsCreatorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(draft=False)

    @action(detail=False, methods=["get"])
    def me(self, request):
        cards = self.queryset.filter(creator=request.user)
        return response.Response(self.serializer_class(cards, many=True).data)


class FollowedUsersListView(ListAPIView):
    """
    Handles /users/followed
    Returns a list of users who the current user follows (excluding blocked follows)
    """

    queryset = User.objects.all()
    serializer_class = FollowerUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.followed_users.filter(
            relationship_as_followed_user__status=FollowRelationship.Status.ACTIVE
        )


class FollowersListView(ListAPIView):
    """
    Handles /users/followers
    Returns a list of users who follow the current user (excluding blocked users)
    """

    queryset = User.objects.all()
    serializer_class = FollowerUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.followed_by.filter(
            relationship_as_follower__status=FollowRelationship.Status.ACTIVE
        )
