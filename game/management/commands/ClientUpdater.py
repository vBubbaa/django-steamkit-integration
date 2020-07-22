import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.client import SteamWorker
from game.models import Game, Task


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

            # If no new changes
            if (currentChangeNumber != getCurrentChangeNumber()):
                for change in changes.app_changes:
                    print("App Change: " + str(change.appid))
                    appid = change.appid
                    # If a task for the app already exists, dont create another task
                    if not Task.objects.filter(appid=appid).exists():
                        # Create a task to edit the existing app
                        Task.objects.create(appid=appid, changenumber=change.change_number)


                # Sets the next change number to the current, so we can check for the next change number
                currentChangeNumber = getCurrentChangeNumber()
                print('current change num after actions ' +
                      str(currentChangeNumber))

            else:
                print("No Changes")

            time.sleep(10)