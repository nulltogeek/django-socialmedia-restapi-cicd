from socialmedia.blog.selectors.posts import get_subscribers
from socialmedia.blog.services.post import unsubscribe, subscribe
from socialmedia.api.mixins import ApiAuthMixin
from socialmedia.api.pagination import LimitOffsetPagination, get_paginated_response
from socialmedia.blog.models import Subscription

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status


class SubscribeDetailApi(ApiAuthMixin, APIView):
    def delete(self, request, username):
        try:
            unsubscribe(user=request.user, username=username)
        except Exception as ex:
            return Response(
                {"detail": "Database Error -" + sre(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response({"detail": "Unsubscribed"}, status=status.HTTP_200_OK)


class SubscribeApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class InputSerializer(serializers.Serializer):
        email = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        email = serializers.CharField()

    class Meta:
        model = Subscription
        fields = ("email",)

    def get_username(self, subscription):
        return subscription.target.email

    @extend_schema(responses=OutputSerializer)
    def get(self, request):
        user = request.user
        query = get_subscribers(user=user)
        return get_paginated_response(
            request=request,
            pagination_class=self.Pagination,
            queryset=query,
            view=self,
        )

    @extend_schema(request=InputSerializer, responses=OutputSerializer)
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # might have a bug here
            query = subscribe(
                user=request.user, email=serializer.validated_data["email"]
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error -" + str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
