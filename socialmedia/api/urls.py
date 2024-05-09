from django.urls import path, include

urlpatterns = [
    path("users/", include(("socialmedia.users.urls", "users"))),
    path("auth/", include(("socialmedia.authentication.urls", "auth"))),
]
