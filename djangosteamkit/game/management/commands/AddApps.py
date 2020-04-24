##############################################
# This import needs to be before the other imports
# See https://github.com/ValvePython/steam/issues/97
import gevent
from gevent import monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
###############################################

from django.core.management.base import BaseCommand, CommandError
from utils.GameHelpers.ModelProcessor import ProcessNewGame, ProcessExistingGame
from utils.GameHelpers.Client import Client
from game.models import Game

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('apps', type=list)
    
    def handle(self, *args, **options):
        # Call the custom client class which handles connecting to the steam client
        client = Client()
        client.login()

        apps = options['apps']

        for app in apps:
            print(str(app))
        # Fake changenum for testing
        changenum = 1337
        ProcessNewGame(client, appid, changenum)