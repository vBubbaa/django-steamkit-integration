import gevent
from binascii import hexlify
from steam.client import SteamClient
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.utils.proto import proto_to_dict
import vdf
import time


class SteamWorker(object):
    def __init__(self):
        self.steam = client = SteamClient()
        client.set_credential_location(".")

        @client.on("error")
        def handle_error(result):
            print("Logon result: %s", repr(result))

        @client.on("connected")
        def handle_connected():
            print("Connected to %s", client.current_server_addr)

        @client.on("disconnected")
        def handle_disconnect():
            print("Disconnected.")
            self.tryReconnect()

    # Attempt reconnects until it succeeds
    def tryReconnect(self):
        connected = False
        fails = 0

        while not connected:
            try:
                self.ClientConnect()
                connected = True
            except Exception as e:
                fails += 1
                print('Reconnection failed with error: ' + str(e))
                print('Failed reconnect attempts: ' + str(fails))
                time.sleep(60)
                pass

    def ClientConnect(self):
        self.steam.anonymous_login()

    def get_product_info(self, appids=[], packageids=[]):
        try:
            resp = self.steam.send_job_and_wait(MsgProto(EMsg.ClientPICSProductInfoRequest),
                                                {
                'apps': map(lambda x: {'appid': x}, appids),
                'packages': map(lambda x: {'packageid': x}, packageids),
            },
                timeout=10
            )

            if not resp:
                return {}

            resp = proto_to_dict(resp)

            for app in resp.get('apps', []):
                app['appinfo'] = vdf.loads(
                    app.pop('buffer')[:-1].decode('utf-8', 'replace'))['appinfo']
                app['sha'] = hexlify(app['sha']).decode('utf-8')
            for pkg in resp.get('packages', []):
                pkg['appinfo'] = vdf.binary_loads(pkg.pop('buffer')[4:])[
                    str(pkg['packageid'])]
                pkg['sha'] = hexlify(pkg['sha']).decode('utf-8')

            return resp
        except Exception as e:
            print('get_product_info() exception: ' + str(e))
            return {}

    def get_product_changes(self, since_change_number):
        try:
            resp = self.steam.send_job_and_wait(MsgProto(EMsg.ClientPICSChangesSinceRequest),
                                                {
                'since_change_number': since_change_number,
                'send_app_info_changes': True,
                'send_package_info_changes': True,
            },
                timeout=10
            )
            return proto_to_dict(resp) or {}
        except Exception as e:
            print('get_product_changes() exception: ' + str(e))
            return {}

    def get_player_count(self, appid):
        resp = self.steam.send_job_and_wait(MsgProto(EMsg.ClientGetNumberOfCurrentPlayersDP),
                                            {'appid': appid},
                                            timeout=10
                                            )
        return proto_to_dict(resp) or {}
