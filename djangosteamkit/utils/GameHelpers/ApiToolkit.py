import requests

"""
get_price() fetches the current price of a game via Steam Api
@params:
    - Appid (the appid of the app we are fetching)
"""


def get_price(appid):
    try:
        priceRequest = requests.get(
            "http://store.steampowered.com/api/appdetails/?appids=" + appid + "&format=json")
        priceRequest = priceRequest.json()

        if priceRequest.get(appid)['success'] == True:
            if priceRequest.get(appid)['data']['is_free'] == True:
                price = 0
            else:
                price = priceRequest.get(
                    appid)['data']['price_overview']['final']
                price = float(str(price)[0:-2] + "." + str(price)[-2:])

    except Exception as e:
        price = None
        print("price exception" + e)

    return price


"""
The steamkit response only gives us the ID of tags,
we have to use the steamapi to get the string value (description) of tags.
Ex (
    steamkit res = "genres": {
                        "0": "1",
                        "1": "37"
                    }
    steam api res = "genres":
                        [
                            {"id":"1","description":"Action"},
                            {"id":"37","description":"Free to Play"}
                        ]
)
See the problem?

@params: 
    - appid (for the game we are getting tags for)
    - tag_type (the type of tag we are getting, ex. genre, category)
    - tag_ids (list of tags we are fetching a description for)
"""


def tag_request(appid, tag_type, tag_ids):
    # try:
    # Initial request and response
    tagRequest = requests.get(
        "http://store.steampowered.com/api/appdetails/?appids=" + appid + "&format=json")
    tagRequest = tagRequest.json()
    # Grab the tag type we are fetching (ex. genre, category)
    request = tagRequest.get(appid)['data'][tag_type]
    # Empty list we will return a list of dicts with the id AND (needed =>) description
    returnList = []

    # For each tag we need to get the description for
    for tag in tag_ids:
        # For each item in the request res, (each item in the list of dicts)
        for item in request:
            # For key and value in items (ex. 'id': 1, 'description': 'Action')
            for k, v in item.items():
                # If the key is 'id' (not description) append the entire dict back (which contains description)
                if (k == 'id' and v == tag):
                    returnList.append(item)

    # Return Fomrat (list of dicts with the id and description):
    # [
    #   {'id': '1', 'description': 'Action'},
    #   {'id': '37', 'description': 'Free to Play'}
    # ]
    #

    return returnList

    # except Exception as e:
    #     print('Oopsies, something went wrong... ' + e)
    #     returnList = None
    #     return returnList


ex = tag_request('730', 'genres', ['1', '37'])
