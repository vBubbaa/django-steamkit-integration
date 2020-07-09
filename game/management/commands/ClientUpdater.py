import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.ModelProcessor import ModelProcessor
from utils.client import SteamWorker
from utils.SteamApiHandler import SteamApi
from game.models import Game


"""
This Django management command serves as a method of continuously running and monitoring
client changes which updates the game objects in our database

Usage:
- python manage.py ClientUpdater
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Steamkit client
        worker = SteamWorker()
        worker.login()

        # Our model processor to process games
        processor = ModelProcessor()

        # Api object to handle api calls (needed for our model processor class)
        api = SteamApi()

        """
        - This function grabs the current change number that the steam client is on
        - The script will use this to check for new change numbers
        """
        def getCurrentChangeNumber():
            changes = worker.get_changes(1)
            currentChangeNum = changes.current_change_number
            return currentChangeNum

        # The current change number out script is on
        # This is the init where we set it to the current number on the steam client
        # - 1 for testing, so we always have fresh changes to look at
        currentChangeNumber = getCurrentChangeNumber()

        # Loop forever to monitor client changes, waits 10 seconds to check for new changes
        while True:
            # Sets the changes to always be at the current change number in our script
            changes = worker.get_changes(currentChangeNumber)

            print('after change declaration hit')

            # If no new changes
            if (currentChangeNumber != getCurrentChangeNumber()):
                print("Changes have occured")
                print('Changes: ' + str(changes))
                for change in changes.app_changes:
                    print("App Change: " + str(change.appid))
                    # If App exists, update it
                    if (Game.objects.filter(appid=change.appid).exists()):
                        print("Game exists")
                        appid = change.appid
                        processor.processExistingGame(appid, change.change_number, worker, api)
                    # If app doesnt exist, create it
                    else:
                        print('Game does not exist')
                        appid = change.appid
                        processor.processNewGame(appid, change.change_number, worker, api)

                # Sets the next change number to the current, so we can check for the next change number
                currentChangeNumber = getCurrentChangeNumber()
                print('current change num after actions ' +
                      str(currentChangeNumber))

            else:
                print("No Changes")

            time.sleep(10)