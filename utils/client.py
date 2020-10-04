import gevent
from binascii import hexlify
from steam.client import SteamClient
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.utils.proto import proto_to_dict
import vdf
from djangosteamkit.secrets import SC_STEAM_LOGIN


class SteamWorker(object):
    def __init__(self):
        self.logged_on_once = False

        self.steam = client = SteamClient()
        client.set_credential_location(".")

        @client.on("error")
        def handle_error(result):
            print("Logon result: %s", repr(result))

        @client.on("connected")
        def handle_connected():
            print("Connected to %s", client.current_server_addr)

        @client.on("channel_secured")
        def send_login():
            if self.logged_on_once and self.steam.relogin_available:
                self.steam.relogin()

        @client.on("logged_on")
        def handle_after_logon():
            self.logged_on_once = True

            print("-"*30)
            print("Logged on as: %s", client.user.name)
            print("Community profile: %s", client.steam_id.community_url)
            print("Last logon: %s", client.user.last_logon)
            print("Last logoff: %s", client.user.last_logoff)
            print("-"*30)

        @client.on("disconnected")
        def handle_disconnect():
            print("Disconnected.")

            if self.logged_on_once:
                print("Reconnecting...")
                client.reconnect(maxdelay=30)

        @client.on("reconnect")
        def handle_reconnect(delay):
            print("Reconnect in %ds...", delay)

        @client.on('auth_code_required')
        def auth_code_prompt(is_2fa, mismatch):
            if is_2fa:
                code = input("Enter 2FA Code: ")
                client.login(two_factor_code=code, **SC_STEAM_LOGIN)
            else:
                code = input("Enter Email Code: ")
                client.login(auth_code=code, **SC_STEAM_LOGIN)

    def client_login(self):
        self.steam.login(**SC_STEAM_LOGIN)

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
