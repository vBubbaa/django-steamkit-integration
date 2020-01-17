from steam.client import SteamClient
from bs4 import BeautifulSoup

"""
The GameSteamKit() class is used for interacting with Steamkit's python port interacting with the
Steam client to gather information

@globals
    - client: Steamkits client instantiation so that we can interact with the Steam client

@params
    - appid: the appid of the game in which you are trying to gather information
"""
class GameSteamkit:
    global client
    client = SteamClient()
    client.anonymous_login()

    def __init__(self, appid):
        self.appid = appid

    """
    get_all_product_info()
    - A method that returns all product information for a specified appid
    - Mainly used for testingpurposes as it doesn't parse out any information from the response
    """
    def get_all_product_info(self):
        return client.get_product_info([self.appid])

    def get_product_info(self):
        res = client.get_product_info([self.appid])
        name = res['apps'][self.appid]['common']['name']
        return name

    def get_price(self):


game = GameSteamkit(440)
print(game.get_all_product_info())
print(game.get_product_info())
