from django.db import transaction
from .models import BaseUser, Profile
from django.core.cache import cache


def create_profile(*, user: BaseUser, bio: str | None) -> Profile:
    return Profile.objects.create(user=user, bio=bio)


def create_user(*, email: str, password: str) -> BaseUser:
    return BaseUser.objects.create_user(email=email, password=password)


@transaction.atomic
def register(*, bio: str | None, email: str, password: str) -> BaseUser:

    user = create_user(email=email, password=password)
    create_profile(user=user, bio=bio)

    return user


def profile_count_update():
    print("Profile count update task")
    profiles = cache.keys("profile_*")

    for profile_key in profiles:
        email = profile_key.replace("profile_", "")
        data = cache.get(profile_key)

        try:
            profile = Profile.objects.get(user__email=email)
            print(profile)

            profile.posts_count = data["posts_count"]
            profile.subscriber_count = data["subscriber_count"]
            profile.subscription_count = data["subscription_count"]
            profile.save()

        except Exception as e:
            print(e)
            continue
