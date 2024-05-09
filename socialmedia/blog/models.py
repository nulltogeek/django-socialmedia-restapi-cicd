from django.db import models
from django.core.exceptions import ValidationError
from socialmedia.common.models import BaseModel
from socialmedia.users.models import BaseUser


class Post(BaseModel):
    slug = models.SlugField(max_length=100, primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(BaseUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.slug


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, related_name="subscriber"
    )
    target = models.ForeignKey(
        BaseUser, on_delete=models.CASCADE, related_name="targets"
    )

    class Meta:
        unique_together = ("subscriber", "target")

    def clean(self):
        if self.subscriber == self.target:
            raise ValidationError("You cannot subscribe to yourself")

    def __str__(self):
        return f"{self.subscriber.email} - {self.target.email}"
