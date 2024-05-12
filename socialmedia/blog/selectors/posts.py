from django.db.models import QuerySet
from socialmedia.blog.models import Post, Subscription
from socialmedia.users.models import BaseUser
from socialmedia.blog.filters import PostFilter


def get_subscribers(*, user: BaseUser) -> QuerySet[Subscription]:
    return Subscription.objects.filter(subscriber=user)


def post_detail(
    *, slug: str, user: BaseUser, self_include: bool = True
) -> QuerySet[Post]:
    # IDs of users that the current user is subscribed to
    subscriptions = list(
        Subscription.objects.filter(subscriber=user).values_list("target", flat=True)
    )
    if self_include:
        subscriptions.append(user.id)
    return Post.objects.get(slug=slug, author_id__in=subscriptions)


def post_list(
    *, filters=None, user: BaseUser, self_include: bool = True
) -> QuerySet[Post]:
    filters = filters or {}
    subscriptions = []
    try:
        subscriptions.extend(
            Subscription.objects.filter(subscriber=user).values_list("target", flat=True)
        )
        if self_include:
            subscriptions.append(user.id)
        if subscriptions:
            qs = Post.objects.filter(author__in=subscriptions)
            return PostFilter(filters, qs).qs
    except Exception as e:
        # Handle the exception gracefully, e.g., log the error
        print(f"An error occurred: {e}")
    return Post.objects.none()

