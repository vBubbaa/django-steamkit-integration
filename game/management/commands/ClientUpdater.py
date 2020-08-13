import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.client import SteamWorker
from game.models import Game, Task


# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# This Django management command serves as a method of continuously running and monitoring steam
# client changes. We get the change numbers and the appids affected and create a task to see when changed.
#
# Usage:
# - python manage.py ClientUpdater
# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('*'*30)
        print('Starting SteamWorker')
        worker = SteamWorker()
        worker.login()
        if worker.isConnected():
            print('Connected')
        else: 
            print('Connection Error')
        print('*'*30)

        print('Get changed')
        currentChangeNum = worker.get_product_changes(0)['current_change_number']

        while True:
            if worker.isConnected():
                changes = worker.get_product_changes(currentChangeNum)
                if currentChangeNum != changes['current_change_number']:
                    print('Changes have occured')
                    if changes.get('app_changes'):
                        for change in changes.get('app_changes'):
                            print(str(change))
                            appid = change['appid']
                            # CHeck if the app alrady has a task
                            if not Task.objects.filter(appid=appid).exists():
                                # Create a task with the app
                                Task.objects.create(appid=appid, changenumber=change['change_number'])
                                print('Task created for appid: ' + str(appid))
                        currentChangeNum = changes['current_change_number']
                else:
                    print('No changes occured')
                    time.sleep(10)
            else:
                print('Disconnected, waiting for reconnect..')
                time.sleep(10)
            

        
        