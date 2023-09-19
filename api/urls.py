from django.contrib import admin
from django.urls import path, include
from .views import CardViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

router = routers.DefaultRouter()
router.register("cards", CardViewSet, basename="cards")
from .views import FollowedUsersListView, FollowersListView


urlpatterns = [
    path("", include(router.urls)),
    path("users/followed", FollowedUsersListView.as_view(), name="followed"),
    path("users/followers", FollowersListView.as_view(), name="followers"),
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
