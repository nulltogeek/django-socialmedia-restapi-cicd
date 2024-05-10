from django.urls import reverse

from socialmedia.api.pagination import (
    LimitOffsetPagination,
    get_paginated_response_context,
)
from socialmedia.blog.models import Post
from socialmedia.api.mixins import ApiAuthMixin
from socialmedia.blog.services import create_post
from socialmedia.blog.selectors import post_list, post_detail

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema


class PostApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class FilterSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255, required=False)
        search = serializers.CharField(max_length=255, required=False)
        created_at__range = serializers.CharField(max_length=255, required=False)
        author__in = serializers.CharField(max_length=255, required=False)
        slug = serializers.CharField(max_length=255, required=False)
        content = serializers.CharField(max_length=255, required=False)

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(max_length=255)
        content = serializers.CharField(max_length=255)

    class OutputSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField("get_author")
        url = serializers.SerializerMethodField("get_url")

        class Meta:
            model = Post
            fields = (
                "title",
                "author",
                "url",
            )

        def get_author(self, post):
            return post.author.username

        def get_url(self, post):
            request = self.context.get("request")
            path = reverse("api:blog:post-detail", args=(post.slug,))
            return request.build_absolute_uri(path)

    @extend_schema(
        request=InputSerializer,
        responses=OutputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            query = create_post(
                user=request.user,
                # might have a bug
                content=serializer.validated_data["content"],
                title=serializer.validated_data["title"],
            )
        except Exception as ex:
            return Response(
                {"detail": "Database Error -" + str(ex)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            self.OutputSerializer(query, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(responses=OutputSerializer, parameters=[FilterSerializer])
    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        try:
            query = post_list(
                filters=filters_serializer.validated_data, user=request.user
            )
        except Exception as ex:
            return Response(
                {"detail": "Filter Error -" + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return get_paginated_response_context(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=query,
            request=request,
            view=self,
        )


class PostDetailApi(ApiAuthMixin, APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    class OutputSerializer(serializers.ModelSerializer):
        author = serializers.SerializerMethodField("get_author")

        class Meta:
            model = Post
            fields = (
                "author",
                "slug",
                "title",
                "content",
                "created_at",
                "updated_at",
            )

        def get_author(self, post):
            return post.author.username

        def get_url(self, post):
            request = self.context.get("request")
            path = reverse("api:blog:post-detail", args=(post.slug,))
            return request.build_absolute_uri(path)

    @extend_schema(responses=OutputSerializer)
    def get(self, request, slug):
        try:
            query = post_detail(
                slu=slug,
                user=user.request,
            )
        except Exception as ex:
            return Response(
                {"detail": "Filter Error -" + str(ex)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.OutputSerializer(query)
        return Response(
            serializer.data,
        )
