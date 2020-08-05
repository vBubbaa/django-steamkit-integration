import time
from django.core.management.base import BaseCommand, CommandError
from game.models import Task


"""
This Django management command clears the task list in our DB to prevent backlogs of tasks if our model processor fails.
This should only be used in testing, not after release
(We shouldn't have a backlog once released because our model processor shouldn't crash and have our tasks keep populating.)

Usage:
- python manage.py TaskClear
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        Task.objects.all().delete()
        


        