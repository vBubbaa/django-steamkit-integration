import requests

"""
The ApiToolKit is a class written in order to make API requests in a simple and effective manner

@params
    - appid: the appid of the game in which you are trying to gather information
"""
class ApiToolkit:

    def __init__(self, appid):
        self.appid = str(appid)

    """
    get_price()
    - returns the price of a specified game through the appdetails steam api endpoint
    """
    def get_price(self):
        priceRequest = requests.get("http://store.steampowered.com/api/appdetails/?appids=" + self.appid + "&format=json")
        priceRequest = priceRequest.json()

        if priceRequest.get(self.appid)['success'] == True:
            if priceRequest.get(self.appid)['data']['is_free'] == True:
                price = 0
            else:
                price = priceRequest.get(self.appid)['data']['price_overview']['final']
                price = float(str(price)[0:-2] + "." + str(price)[-2:])

        return price

game = ApiToolkit(710920)
print(game.get_price())
