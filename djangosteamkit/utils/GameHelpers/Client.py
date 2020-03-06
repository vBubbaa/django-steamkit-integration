import faulthandler
from utils.GameHelpers.ApiToolkit import get_price
from django.utils.text import slugify
from steam.enums import EResult
from steam.client import SteamClient

# Debug segmentation faults
faulthandler.enable()


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
    """

    def get_all_product_info(self, appid):
        res = client.get_product_info([appid])
        print(res)

        try:
            price = get_price(str(appid))
        except Exception as e:
            print('price exception: ' + str(e))
            price = None

        # If we dont get the common section, we dont have access to the information
        try:
            # Constansts that might return null
            # If they do return null we just pass it as a None value
            oslist = res['apps'][appid]['common'].get('oslist', None)
            releasestate = res['apps'][appid]['common'].get(
                'releasestate', None)
            icon = res['apps'][appid]['common'].get('icon', None)
            logo = res['apps'][appid]['common'].get('logo', None)
            logo_small = res['apps'][appid]['common'].get('logo_small', None)
            clienticon = res['apps'][appid]['common'].get('clienticon', None)
            languages = res['apps'][appid]['common'].get(
                'supported_languages', None)
            app_type = res['apps'][appid]['common'].get(
                'type', None)
            controller_support = res['apps'][appid]['common'].get(
                'controller_support', None)
            associations = res['apps'][appid]['common'].get(
                'associations', None)
            primary_genre = res['apps'][appid]['common'].get(
                'primary_genre', None)
            genres = res['apps'][appid]['common'].get(
                'genres', None)
            category = res['apps'][appid]['common'].get(
                'category', None)
            steam_release_date = res['apps'][appid]['common'].get(
                'steam_release_date', None)
            metacritic_score = res['apps'][appid]['common'].get(
                'metacritic_score', None)
            metacritic_fullurl = res['apps'][appid]['common'].get(
                'metacritic_fullurl', None)

            # Dictionary we pass to the updater to save as values into our DB
            info = {
                'name': res['apps'][appid]['common']['name'],
                'slug': slugify(res['apps'][appid]['common']['name'], allow_unicode=True),
                'price': price,
                'oslist': oslist,
                'releasestate': releasestate,
                'icon': icon,
                'logo': logo,
                'logo_small': logo_small,
                'clienticon': clienticon,
                'languages': languages,
                'app_type': app_type,
                'controller_support': controller_support,
                'associations': associations,
                'primary_genre': primary_genre,
                'genres': genres,
                'category': category,
                'steam_release_date': steam_release_date,
                'metacritic_score': metacritic_score,
                'metacritic_fullurl': metacritic_fullurl,
            }

        # If there is not information available return None
        except Exception as e:
            print('#######################################################')
            print('client exception: ' + str(e))
            print('#######################################################')
            info = None

        return info

    """
    - Gets the changes from the client from a previous change number
    """

    def get_changes(self, change_num):
        return client.get_changes_since(change_number=change_num, app_changes=True, package_changes=False)
