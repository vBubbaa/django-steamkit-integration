import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from django.core.management.base import BaseCommand, CommandError
from utils.SteamApiHandler import SteamApi
from utils.ModelProcessor import ModelProcessor
from utils.client import SteamWorker

"""
This Django management command is for test usage for to either create a single app in our database,
or update an existing app in our database. Either call processNewGame() or processExistingGame()
on the processor object depending on which of the two you would like to do

Usage:
- python manage.py AppTest
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Appid to work with (either create new app in db, or edit update app)
        appid = 449470

        # Necessary objects we need to process app from steamkit
        # - api handler
        # - steamkit worker (and login)
        # - our model processor
        api = SteamApi()
        worker = SteamWorker()
        worker.login()
        processor = ModelProcessor()

        # Fake changenumber for test model processor command 
        changenum = 1337

        # Call processNewGame, or processExistingGame depending on you want to create
        # a new app in the db, or update and existing app in the DB
        processor.processNewGame(appid, changenum, worker, api)