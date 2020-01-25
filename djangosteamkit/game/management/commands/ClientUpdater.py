from utils.GameHelpers.Client import Client
from game.models import Game, GameChange
from django.core.management.base import BaseCommand, CommandError
import time

"""
This Django management command serves as a method of continuously running and monitoring
client changes which updates the game objects in our database

Usage:
- python manage.py ClientUpdater
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Call the custom client class which handles connecting to the steam client
        client = Client()
        client.login()

        # An initial change number to start working at
        initialChangeNum = 7612318

        # initial changes based on the initial change number
        changes = client.get_changes(initialChangeNum)

        # The current change number we are on
        currentChangeNum = changes.since_change_number

        # The next change number
        nextChangeNum = changes.current_change_number

        # Loop forever to monitor client changes, waits 10 seconds to check for new changes
        while True:
            # Set the changes to the current change number
            # changes = client.get_changes(currentChangeNum)

            print("################### changes ###################")
            print("Current: " + str(currentChangeNum))
            print("Next: " + str(nextChangeNum))

            # If no new changes
            if (currentChangeNum != nextChangeNum):
                print("Changes have occured")
                for change in changes.app_changes:
                    print("App Change: " + str(change.appid))
                    # If App exists, update it
                    if (Game.objects.filter(appid=change.appid).exists()):
                        print("Game exists")
                    # If app doesnt exist, create it
                    else:
                        print('Game does not exist')
                        appid = change.appid
                        print(str(appid))
                        gameInfo = client.get_all_product_info(appid)
                        print(gameInfo)
                        game = Game(appid=appid, name=gameInfo['name'], slug=gameInfo['slug'], price=gameInfo['price'])
                        game.save()

                        print("Change Number " + str(change.change_number) + ' registered.')

                # Sets the next change number to the current, so we can check for the next change number
                currentChangeNum = nextChangeNum

                # Set changes to the new current change number
                changes = client.get_changes(currentChangeNum)
                time.sleep(1)

            else:
                print("No Changes")

            time.sleep(10)
