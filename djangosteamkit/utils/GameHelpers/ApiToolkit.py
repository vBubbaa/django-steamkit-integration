import requests

def get_price(appid):
    try:
        priceRequest = requests.get("http://store.steampowered.com/api/appdetails/?appids=" + appid + "&format=json")
        priceRequest = priceRequest.json()

        if priceRequest.get(appid)['success'] == True:
            if priceRequest.get(appid)['data']['is_free'] == True:
                price = 0
            else:
                price = priceRequest.get(appid)['data']['price_overview']['final']
                price = float(str(price)[0:-2] + "." + str(price)[-2:])
    except Exception as e:
        print('price exception ' + e)
        price = None

    return price
