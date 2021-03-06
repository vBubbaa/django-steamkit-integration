from game.models import Game, Task
from utils.SteamApiHandler import SteamApi
from utils.client import SteamWorker
from utils.ModelProcessor import ModelProcessor
from django.core.management.base import BaseCommand, CommandError
import time
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()


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
            if worker.isConnected():
                # See if there are any tasks
                if Task.objects.all():
                    # Loop through each task and start processing them
                    for task in Task.objects.all():
                        # If the app already exists, we update it with processExistingGame()
                        if Game.objects.filter(appid=task.appid).exists():
                            print('task is an existing app | appid: ' +
                                  str(task.appid))
                            task.processing = True
                            processor.processExistingGame(
                                task.appid, task.changenumber, worker, api)
                            task.delete()
                        # if the app doesn't exist, we create a new app with processNewGame
                        else:
                            print('task is New app | appid: ' + str(task.appid))
                            task.processing = True
                            processor.processNewGame(
                                task.appid, task.changenumber, worker, api)
                            task.delete()

                        time.sleep(10)
                else:
                    print('Task model has NO tasks')
                    time.sleep(10)
            else:
                print('Disconnected from steam, waiting for reconnect...')
                time.sleep(10)
