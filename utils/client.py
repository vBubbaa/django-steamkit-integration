from steam.client import SteamClient
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.utils.proto import proto_to_dict
import logging
import gevent
from binascii import hexlify
import logging
import vdf


class SteamWorker(object):
    def __init__(self):
        self.steam = client = SteamClient()
        self.logged_on_once = False

        @client.on("error")
        def handle_error(result):
            print("Logon result: %s", repr(result))

        @client.on("connected")
        def handle_connected():
            print("Connected to %s", client.current_server_addr)

        @client.on("logged_on")
        def handle_after_logon():
            self.logged_on_once = True

            print("logged in successfully to steamkit")

        @client.on("disconnected")
        def handle_disconnect():
            print("Disconnected.")

            if self.logged_on_once:
                print("Reconnecting...")
                client.reconnect(maxdelay=30)

    def login(self):
        self.steam.anonymous_login()

    def close(self):
        if self.steam.logged_on:
            self.logged_on_once = False
            print("Logout")
            self.steam.logout()
        if self.steam.connected:
            self.steam.disconnect()

    def get_product_info(self, appids=[]):'
        try:
            resp = self.steam.send_job_and_wait(MsgProto(EMsg.ClientPICSProductInfoRequest),
                                                {
                'apps': map(lambda x: {'appid': x}, appids),
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

            return resp
        except Exception as e:
            print('Error in get_production_info ' + str(e) )

    def get_changes(self, change_num):
        return self.steam.get_changes_since(change_number=change_num, app_changes=True, package_changes=False)
