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
    # Init global vars
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Model Processor Instance
        self.processor = ModelProcessor()
        # In house API wrapper instance
        self.api = SteamApi()
        # Client object
        self.client = SteamWorker()

    def handle(self, *args, **options):
        print('-'*30)
        print('Starting Scout...')
        self.client.steam.anonymous_login()
        print('Login Successful.')
        print('-'*30)

        # Get the current changelog to start from
        currentChangeNum = self.client.get_product_changes(0)['current_change_number']

        # Start mointoring changelogs
        while True:
            if self.client.steam.connected:
                # First, check for exists tasks to process first.
                self.handleTasks()
                # Get the changes from the current change number
                changes = self.client.get_product_changes(currentChangeNum)
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
                            
                            self.handleProcessDispatch(appid, change['change_number'])

                            # Timeout for 10 seconds to avoid excessive requests.
                            time.sleep(10)

                        # Set the new changenumber
                        currentChangeNum = changes['current_change_number']

                # No changes have occured, wait 10 seconds to rescan steam.
                else:
                    print('No Changes have occured')
                    time.sleep(60)

            # Connection error occured, wait 10 seconds before retrying.
            else:
                print('Steam Connection Error. client.isConnected() returned false.')
                time.sleep(10)

    # Iterate tasks and process those apps (not from PICSChanges)
    def handleTasks(self):
        # See if any tasks exist
        if Task.objects.all():  
            print('Tasks are in queue, startin processing')
            for task in Task.objects.all():
                # Dispatch the app, then delete the task 
                self.handleProcessDispatch(task.appid, task.changenumber)
                task.delete()

    # Grabs app info via steam and dispatches the payload to be processed via model processor
    def handleProcessDispatch(self, appid, changenumber):
        # Grab app info from steam client
        payload = self.client.get_product_info([appid])

        # Check for payload faults
        if payload == None or 'apps' not in payload or 'appinfo' not in payload['apps'][0] or 'common' not in payload['apps'][0]['appinfo']:
            # Log appid, change data, payload data
            print('Skipping due to insufficient response data for app: ' + str(appid) + ' and change data: ' + str(changenumber))
        
        # If there is valid response data, send the request to process it with out model processor
        else:
            # Check if the game exists in our db so we can either process existing, or process new
            # If game exists in our DB
            if Game.objects.filter(appid=appid):
                self.processor.processExistingGame(appid, changenumber, self.api, payload)
            # Game does not exist in our DB
            else:
                self.processor.processNewGame(appid, changenumber, self.api, payload)

        
        