import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.client import SteamWorker
from game.models import Game, Task
from utils.ClientMonitor import ClientMonitor


# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# This Django management command serves as a method of continuously running and monitoring steam
# client changes. We get the change numbers and the appids affected and create a task to see when changed.
#
# Usage:
# - python manage.py ClientUpdater
# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('~ Steam Monitor ~')
        print('~'*30)
        print('Starting client monitor..')
        cm = ClientMonitor()
        print('Client Monitor started succesfully')

        print('Logging in..')
        cm.tryLogin()

        print('Getting current change number..')
        cm.getCurrentChangeNumber()
        print('Set current change number to: ' + str(cm.currentChangeNumber))

        # Actual client monitor running forever with sleeps to prevent excessive requests.
        while True:
            cm.changeMonitor()
            time.sleep(10)

        