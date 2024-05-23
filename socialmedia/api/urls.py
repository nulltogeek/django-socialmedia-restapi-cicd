from django.urls import path, include


app_name = "api"

urlpatterns = [
    path("users/", include(("socialmedia.users.urls", "users"))),
    path("auth/", include(("socialmedia.authentication.urls", "authentication"))),
    path("blog/", include(("socialmedia.blog.urls", "blog"))),
]
