import pytest
import json

from django.test import Client
from django.urls import reverse

from rest_framework.test import APIClient

from socialmedia.users.models import BaseUser


@pytest.mark.django_db
def test_unath_post_api(user1, subscription1, profile1, post1):
    client = Client()
    url_ = reverse("api:blog:post")
    response = client.post(url_, content_type="application/json")
    assert response.status_code == 401


@pytest.mark.django_db
def test_auth_api(api_client, user1, subscription1, profile1, post1):
    url_ = reverse("api:blog:post")
    response = api_client.get(url_, content_type="application/json")
    assert response.status_code == 200


@pytest.mark.django_db
def test_login(user1, subscription1, profile1, post1):
    user = BaseUser.objects.create_user(email="js@js.com", password="js.sj")
    api_client = APIClient()
    url_ = reverse("api:authentication:jwt:login")
