from celery import shared_task
from .services import profile_count_update


@shared_task
def profile_count_update_task():
    profile_count_update()
