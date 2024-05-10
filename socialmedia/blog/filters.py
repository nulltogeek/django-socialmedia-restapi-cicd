from django_filters import (
    CharFilter,
    FilterSet,
)
from django.contrib.postgres.search import SearchVector
from django.utils import timezone

from socialmedia.blog.models import Post

from rest_framework.exceptions import APIException


class PostFilter(FilterSet):
    search = CharFilter(method="search_filter")
    author__in = CharFilter(method="author_filter__in")
    created_at__range = CharFilter(
        method="created_at_filter__range",
    )

    def filter_author__in(self, queryset, name, value):
        limit = 10
        authors = value.split(",")
        if len(authors) > limit:
            raise APIException(f"You cannot add more than {limit} usernames")
        return queryset.filter(author__username__in=authors)

    def filter_created_at__range(self, queryset, name, value):
        limit = 2
        created_at__in = value.split(",")
        if len(created_at__in) > limit:
            raise APIException(f"Please just provide two dates")

        created_at_0, created_at_1 = created_at__in

        if not created_at_1:
            created_at_1 = timezone.now()

        if not created_at_0:
            created_at_0 = timezone.now()
            return queryset.filter(created_at__date__lt=created_at_1)

        return queryset.filter(created_at__date__range=(created_at_0, created_at_1))

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("title"),
        ).filter(search=value)

    class Meta:
        model = Post
        fields = (
            "slug",
            "title",
        )
