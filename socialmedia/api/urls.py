from django.urls import path, include

urlpatterns = [
    path("users/", include(("socialmedia.users.urls", "users"))),
]
