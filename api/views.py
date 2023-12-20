from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, response, status, filters
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    ListCreateAPIView,
)
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from .models import Card, User, FollowRelationship, CardStyleDeclaration
from .serializers import (
    CardSerializer,
    FollowerUserSerializer,
    FollowRelationshipSerializer,
    CardStyleDeclarationSerializer,
)
from .permissions import IsCreatorOrReadOnly


class CardViewSet(viewsets.ModelViewSet):
    """
    Handle retrieve, create, edit, and destroy for cards.
    Allow full-text search on title, body, and tags via ?search=term.
    """

    queryset = Card.objects.all().order_by("-created_at")
    serializer_class = CardSerializer
    permission_classes = [IsCreatorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["front_text", "back_text", "creator__username"]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(draft=False)

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False)
    def me(self, request):
        if not request.user.is_authenticated:
            return response.Response(
                {"error": "You need to be logged in."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
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


class CardStyleDeclarationListCreateView(ListCreateAPIView):
    """
    Get or create a style declaration for a card. The card must belong to the logged in user in order to save styles for it.
    Properties and values are not validated to be valid CSS properties or values. If a property already exists, it will be ignored.
    To update properties, use the PATCH method.
    """

    queryset = CardStyleDeclaration.objects.all()
    serializer_class = CardStyleDeclarationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs["card_pk"])
        if card.creator != self.request.user:
            raise ValidationError(
                "You must be the author of the card to save styles for it."
            )
        serializer.save(card=card)

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class CardStyleDeclarationUpdateView(UpdateAPIView):
    """
    Update a style declaration for a card. The card must belong to the logged in user in order to save styles for it.
    Properties and values are not validated to be valid CSS properties or values.
    The body of the request should be an array of objects with the following shape:
    [
        {
            "property": "property-name",
            "value": "property-value",
            "boolValue": true
        }
    ]
    """

    queryset = CardStyleDeclaration.objects.all()
    serializer_class = CardStyleDeclarationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        return get_object_or_404(
            self.request.user.cards.all(), pk=self.kwargs["card_pk"]
        )

    def perform_update(self, serializer):
        card = Card.objects.get(pk=self.kwargs["card_pk"])
        if card.creator != self.request.user:
            raise ValidationError(
                "You must be the author of the card to save styles for it."
            )
        if not isinstance(serializer.validated_data, list):
            serializer.validated_data = [serializer.validated_data]
        serializer.save(card=card)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, many=True, **kwargs)
