import gevent.monkey
gevent.monkey.patch_all()

import time
from django.core.management.base import BaseCommand, CommandError
from utils.client import SteamWorker

# # # # # # # # # # # # # # # # # # # # # # # # # # 
# Test the steam client login
# Will be needed to run manually and let steam remember our device
# After this is ran, the auto-script can reconnect automatically
# # # # # # # # # # # # # # # # # # # # # # # # # # 
class Command(BaseCommand):
    def handle(self, *args, **options):
        worker = SteamWorker()
        worker.client_login()
        time.sleep(10)
        print(worker.steam.connected)
        time.sleep(5)
        worker.steam.disconnect()
        print(worker.steam.connected)