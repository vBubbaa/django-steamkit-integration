from utils.GameHelpers.Client import Client
from game.models import Game, GameChange, OSOptions
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

        """
        - This function grabs the current change number that the steam client is on
        - The script will use this to check for new change numbers
        """
        def getCurrentChangeNumber():
            changes = client.get_changes(1)
            currentChangeNum = changes.current_change_number
            return currentChangeNum

        # The current change number out script is on
        # This is the init where we set it to the current number on the steam client
        # - 1 for testing, so we always have fresh changes to look at
        currentChangeNumber = getCurrentChangeNumber()

        # Loop forever to monitor client changes, waits 10 seconds to check for new changes
        while True:
            # Sets the changes to always be at the current change number in our script
            changes = client.get_changes(currentChangeNumber)

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
                    # If app doesnt exist, create it
                    else:
                        print('Game does not exist')
                        appid = change.appid
                        print(str(appid))
                        gameInfo = client.get_all_product_info(appid)

                        print('hit before gamInfo')

                        if gameInfo is not None:
                            game = Game(
                                appid=appid,
                                name=gameInfo['name'],
                                slug=gameInfo['slug'],
                                price=gameInfo['price'],
                                release_state=gameInfo['releasestate'],
                                icon=gameInfo['icon'],
                                logo=gameInfo['logo'],
                                logo_small=gameInfo['logo_small'],
                                clienticon=gameInfo['clienticon'],
                                clienttga=gameInfo['clienttga'],
                            )
                            game.save()

                            print('hit after gameinfo')

                            # OS list Stuff
                            oslist = gameInfo['oslist']
                            print('OSLIST@@@@@@@@@@@@@@@@@@@@@@@ ' + str(oslist))
                            if oslist is not None:
                                oslist = gameInfo['oslist'].split(',')
                                for os in oslist:
                                    print("################## OS #######################")
                                    print(os)
                                    if (os == 'windows'):
                                        game.os.add(OSOptions.objects.get(os=OSOptions.WIN))
                                    elif (os == 'macos'):
                                        game.os.add(OSOptions.objects.get(os=OSOptions.MAC))
                                    else:
                                        game.os.add(OSOptions.objects.get(os=OSOptions.LIN))
                                game.save()

                            # Change number stuff
                            gamechange = GameChange(
                                change_number=change.change_number,
                                game=game,
                                changelog=GameChange.changelog_builder(
                                    GameChange.ADD,
                                    game.appid,
                                ),
                                action=GameChange.ADD
                            )
                            gamechange.save()

                            print("Change Number " + str(gamechange.change_number) + ' registered.')
                            time.sleep(.5)
                        else:
                            print('######### no common section, continue on #########')
                            continue

                # Sets the next change number to the current, so we can check for the next change number
                currentChangeNumber = getCurrentChangeNumber()
                print('current change num after actions ' + str(currentChangeNumber))

            else:
                print("No Changes")

            time.sleep(10)
