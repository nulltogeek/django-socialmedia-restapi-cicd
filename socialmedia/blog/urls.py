from django.urls import path, include
from .apis.post import PostApi, PostDetailApi
from .apis.subscriptions import SubscribeApi, SubscribeDetailApi

app_name = "blog"

urlpatterns = [
    path("subscribe/", SubscribeApi.as_view(), name="subscribe"),
    path(
        "unsubscribe/<str:email>/",
        SubscribeDetailApi.as_view(),
        name="subscribe-detail",
    ),
    path("post/", PostApi.as_view(), name="post"),
    path("post/<slug:slug>/", PostDetailApi.as_view(), name="post-detail"),
]
