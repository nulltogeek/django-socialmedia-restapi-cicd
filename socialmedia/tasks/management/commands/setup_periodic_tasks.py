from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import get_default_timezone_name

from django_celery_beat.models import IntervalSchedule, CrontabSchedule, PeriodicTask
from socialmedia.users.tasks import profile_count_update_task


class Command(BaseCommand):
    help = """
    Setup celery beat periodic tasks.

    Following tasks will be created:

        - Profile count update task every 10 seconds
    """

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print("Deleting all periodic tasks and schedules...\n")

        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
        PeriodicTask.objects.all().delete()

        periodic_tasks_data = [
            {
                "task": profile_count_update_task,
                "name": "profile count update task every 10 seconds",
                "interval": {
                    "every": 10,
                    "period": IntervalSchedule.SECONDS,
                },
                "enabled": True,
            },
        ]

        for periodic_task in periodic_tasks_data:
            print(f'Setting up {periodic_task["name"]}')

            interval, created = IntervalSchedule.objects.get_or_create(
                every=periodic_task["interval"]["every"],
                period=periodic_task["interval"]["period"],
            )

            PeriodicTask.objects.create(
                name=periodic_task["name"],
                task=periodic_task["task"].name,
                interval=interval,
                enabled=periodic_task["enabled"],
            )
