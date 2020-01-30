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

        # An initial change number to start working at
        initialChangeNum = 1

        # initial changes based on the initial change number
        changes = client.get_changes(initialChangeNum)

        # The next change number
        nextChangeNum = changes.current_change_number

        # The current change number we are on
        # We set it to the next change number so that we can start monitoring from the current change number
        # next change -1 for testing
        currentChangeNum = nextChangeNum - 1

        changes = client.get_changes(currentChangeNum)

        """
        TODO:
        - Filter game swith releasestate: 'prerelease' to not fetch the price
        - Access game content with user pattern like: https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/570/d4f836839254be08d8e9dd333ecc9a01782c26d2_thumb.jpg
        """

        # Loop forever to monitor client changes, waits 10 seconds to check for new changes
        while True:
            print("################### changes ###################")
            print("Current: " + str(currentChangeNum))
            print("Next: " + str(nextChangeNum))

            # If no new changes
            if (currentChangeNum != nextChangeNum):
                print("Changes have occured")
                print(changes)
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
                        else:
                            print('######### no common section, continue on #########')
                            continue

                # Sets the next change number to the current, so we can check for the next change number
                currentChangeNum = nextChangeNum
                print('current change num after actions ' + str(currentChangeNum))

                # Set changes to the new current change number
                changes = client.get_changes(currentChangeNum)
                time.sleep(10)

            else:
                print("No Changes")

            time.sleep(10)
