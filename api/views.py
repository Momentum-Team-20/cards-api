from django.shortcuts import render
from rest_framework import viewsets, permissions, response
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import Card, User, FollowRelationship
from .serializers import (
    CardSerializer,
    FollowerUserSerializer,
    FollowRelationshipSerializer,
)
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


class FollowRelationshipCreateView(CreateAPIView):
    """
    Creates a follow relationship between the logged in user (the follower) and the user specified in the request body
    """

    queryset = FollowRelationship.objects.all()
    serializer_class = FollowRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except IntegrityError as e:
            if "unique constraint" in str(e):
                raise ValidationError("You already follow this user.")
            raise e
        return super().perform_create(serializer)


class FollowRelationshipDestroyView(DestroyAPIView):
    """
    Unfollow the user specified in the URL path
    """

    queryset = FollowRelationship.objects.all()
    serializer_class = FollowRelationshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "followed_user_id"
    lookup_url_kwarg = "followed_user_pk"

    def get_object(self):
        return self.get_queryset().get(
            follower=self.request.user,
            followed_user_id=self.kwargs[self.lookup_url_kwarg],
        )

    # def perform_destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.follower != request.user:
    #         raise ValidationError("You can only delete your own follow relationships.")
    #     else:
    #         return super().perform_destroy(request, *args, **kwargs)
