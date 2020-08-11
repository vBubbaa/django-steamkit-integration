import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from utils.client import SteamWorker
from game.models import Task


# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# ClientMonitor() Class:
# Our Client Monitor class keeps track of change numbers, can get the current change numbers, logs in, and has the monitor function
# which can be ran to catch changes and get appID details
# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class ClientMonitor():
    # Create a worker object
    # currentChangeNumbr keeps track of the current change number
    def __init__(self):
        self.worker = SteamWorker()
        # Init change number to get most recent changes
        self.currentChangeNumber = None

    # Login to steamkit
    def tryLogin(self):
        self.worker.login()

    # Grabs the most recent chang number
    def getCurrentChangeNumber(self):
        changes = self.worker.get_product_changes(1)
        self.currentChangeNumber = changes['current_change_number']
        print('Current change number from getCurrentChangeNumber(): ' + str(self.currentChangeNumber))
        return self.currentChangeNumber

    def changeMonitor(self):
        try:
            # Sets the changenumber to the current change number
            changes = self.worker.get_product_changes(self.currentChangeNumber)

            # Check if changes have occured
            if (self.currentChangeNumber != self.getCurrentChangeNumber()):
                print('Changes have occured')
                print(str(changes))
                print('~'*30)
                # Check if apps where in the change (we don't care about packages.. yet..)
                if changes.get('app_changes'):
                    for change in changes.get('app_changes'):
                        print('# '*15)
                        print('Change: ' + str(change) + ' | App Change Appid: ' + str(change['appid']))
                        appid = change['appid']
                        # CHeck if the app alrady has a task
                        if not Task.objects.filter(appid=appid).exists():
                            # Create a task with the app
                            Task.objects.create(appid=appid, changenumber=change['change_number'])
                            print('Task created for appid: ' + str(appid))
                        print('# '*15)
            else:
                print('No changes have occured')
        except Exception as e:
            print('Exception with changes: ' + str(e) + ' ' + str(self.currentChangeNumber)