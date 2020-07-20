import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.ModelProcessor import ModelProcessor
from utils.client import SteamWorker
from utils.SteamApiHandler import SteamApi
from game.models import Game, Task


"""
This Django management command constantly monitors our Task objects and if any tasks are created, this command
begins the task of either creating the app, or editing the existing app

Usage:
- python manage.py TaskUpdater
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Steamkit client
        worker = SteamWorker()
        worker.login()

        # Our model processor to process games
        processor = ModelProcessor()
        # Api class to handle steam api requests
        api = SteamApi()

        while True:
            # See if there are any tasks
            if Task.objects.all():
                # Loop through each task and start processing them
                for task in Task.objects.all():
                    if task.action == 'new':
                        print('task is new app')
                        processor.processNewGame(task.appid, task.changenumber, worker, api)
                        task.delete()
                    else:
                        print('task is existing app')
                        processor.processExistingGame(task.appid, task.changenumber, worker, api)
                        task.delete()
            else:
                print('Task model has NO tasks')

            time.sleep(10)


        