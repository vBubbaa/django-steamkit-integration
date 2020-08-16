import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.client import SteamWorker
from game.models import Game, Task
from utils.ModelProcessor import ModelProcessor
from utils.SteamApiHandler import SteamApi


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Experimental use of Steam Client to both monitor changes as well as get app detail information with a single 
# instead of two seperate clients
#
# Usage:
# - python manage.py Scout
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('-'*30)
        print('Starting Scout...')
        
        # Client instance
        client = SteamWorker()

        # Model Processor Instance
        processor = ModelProcessor()

        # In house API wrapper instance
        api = SteamApi()
        
        # Attempt login until the login is successful
        while True:
            try:
                client.login()
                break
            except:
                print('Login failed, waiting for connection...')
                time.sleep(10)
        
        print('Login Successful.')
        print('-'*30)

        # Get the current changelog to start from
        currentChangeNum = client.get_product_changes(0)['current_change_number']

        # Start mointoring changelogs
        while True:
            if client.isConnected():
                # Get the changes from the current change number
                changes = client.get_product_changes(currentChangeNum)
                # Check if changes have occured by comparing change number values
                if currentChangeNum != changes['current_change_number']:
                    print('Changes have occured')
                    # If here, changes have occured
                    # Check if any of the changes where app changes (we aren't tracking any other changes)
                    if changes.get('app_changes'):
                        print('Changes: ' + str(changes.get('app_changes')))
                        # Iterate changes and process each appid
                        for change in changes.get('app_changes'):
                            print(str(change))
                            # Grab the appid of the change so we can get the app deatils.
                            appid = change['appid']
                            payload = client.get_product_info([appid])
                            print(str(payload))

                            # Check for payload faults
                            if payload == None or 'apps' not in payload or 'appinfo' not in payload['apps'][0] or 'common' not in payload['apps'][0]['appinfo']:
                                # Log appid, change data, payload data
                                print('Skipping due to insufficient response data for app: ' + str(appid) + ' and change data: ' + str(change) + ' and payload: ' + str(payload))
                            
                            # If there is valid response data, send the request to process it with out model processor
                            else:
                                # Check if the game exists in our db so we can either process existing, or process new
                                # If game exists in our DB
                                if Game.objects.filter(appid=appid):
                                    processor.processExistingGame(appid, change['change_number'], api, payload)
                                # Game does not exist in our DB
                                else:
                                    processor.processNewGame(appid, change['change_number'], api, payload)

                            # Timeout for 5 seconds to avoid excessive requests.
                            time.sleep(5)

                        # Set the new changenumber
                        currentChangeNum = changes['current_change_number']

                # No changes have occured, wait 10 seconds to rescan steam.
                else:
                    print('No Changes have occured')
                    time.sleep(10)

            # Connection error occured, wait 10 seconds before retrying.
            else:
                print('Steam Connection Error. client.isConnected() returned false.')
                time.sleep(10)



        
        