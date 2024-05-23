import pytest
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from socialmedia.users.models import BaseUser
from socialmedia.tests.factories import (
    BaseUserFactory,
    ProfileFactory,
    SubscriptionFactory,
    PostFactory,
)


@pytest.fixture
def api_client():
    user = BaseUser.objects.create_user(
        email="example@gmail.com", password="password@123"
    )
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def user1():
    return BaseUserFactory()


@pytest.fixture
def user2():
    return BaseUserFactory()


@pytest.fixture
def profile1(user1):
    return ProfileFactory(user=user1)


@pytest.fixture
def subscription1(user1, user2):
    return SubscriptionFactory(target=user1, subscriber=user2)


@pytest.fixture
def post1(user1):
    return PostFactory(author=user1)
