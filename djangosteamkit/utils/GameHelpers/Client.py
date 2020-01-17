from steam.client import SteamClient
from steam.enums import EResult

class Client:

    global client
    client = SteamClient()

    @client.on("error")
    def handle_error(result):
        print("Logon result: %s", repr(result))

    @client.on("channel_secured")
    def send_login():
        if client.relogin_available:
            client.relogin()

    @client.on("connected")
    def handle_connected():
        print("Connected to %s", client.current_server_addr)

    @client.on("reconnect")
    def handle_reconnect(delay):
        print("Reconnect in %ds...", delay)

    @client.on("disconnected")
    def handle_disconnect():
        print("Disconnected.")

        if client.relogin_available:
            print("Reconnecting...")
            client.reconnect(maxdelay=30)

    @client.on("logged_on")
    def handle_after_logon():
        print("-"*30)
        print("Logged on as: %s", client.user.name)
        print("Community profile: %s", client.steam_id.community_url)
        print("Last logon: %s", client.user.last_logon)
        print("Last logoff: %s", client.user.last_logoff)
        print("-"*30)
        print("Press ^C to exit")

    """
    - Performs a login to the Steam client with an anonymous login
    """
    def login(self):
        client.anonymous_login()

    """
    - A method that returns all product information for a specified appid
    - Mainly used for testingpurposes as it doesn't parse out any information from the response
    """
    def get_all_product_info(self, appid):
        return client.get_product_info([appid])

    def get_product_info(self, appid):
        res = client.get_product_info([appid])
        name = res['apps'][appid]['common']['name']
        return name

    """
    - Gets the changes from the client from a previous change number
    """
    def get_changes(self, change_num):
        return client.get_changes_since(change_number = change_num, app_changes=True, package_changes=False)
