from django.contrib import admin
from django.urls import path, include
from .views import CardViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

router = routers.DefaultRouter()
router.register("cards", CardViewSet, basename="cards")
from .views import (
    FollowedUsersListView,
    FollowersListView,
    FollowRelationshipCreateView,
    FollowRelationshipDestroyView,
    CardStyleDeclarationListCreateView,
    CardStyleDeclarationUpdateView,
)


urlpatterns = [
    path("", include(router.urls)),
    path(
        "cards/<int:card_pk>/styles/",
        CardStyleDeclarationListCreateView.as_view(),
        name="card-styles",
    ),
    path(
        "cards/<int:card_pk>/styles/edit/",
        CardStyleDeclarationUpdateView.as_view(),
        name="card-style-edit",
    ),
    path("users/followed", FollowedUsersListView.as_view(), name="followed"),
    path("users/followers", FollowersListView.as_view(), name="followers"),
    path("follows/", FollowRelationshipCreateView.as_view(), name="follows"),
    path(
        "unfollow/<int:followed_user_pk>/",
        FollowRelationshipDestroyView.as_view(),
        name="unfollow",
    ),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(
            template_name="drf_spectacular/swagger_ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
]
