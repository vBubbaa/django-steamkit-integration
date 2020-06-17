import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

import requests
from django.conf import settings


class SteamApi():
    def __init__(self):
        self.key = '?key=29ADA8FE335052FE66A32EEB043ABA31'
        self.baseurl = 'http://api.steampowered.com'
        self.format = '&format=json'

    def getUserLibrary(self, steamid):
        method = '/IPlayerService/GetOwnedGames/v0001/'
        url = self.baseurl + method + self.key + \
            '&steamid=' + str(steamid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    def getVacInfo(self, steamid):
        method = '/ISteamUser/GetPlayerBans/v1/'
        url = self.baseurl + method + self.key + '&steamids=' + str(steamid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    # Gets a players profile details (personaname, picture, etc.)
    def getUserDetails(self, steamid):
        method = '/ISteamUser/GetPlayerSummaries/v001/'
        url = self.baseurl + method + self.key + '&steamids=' + str(steamid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    # Gets a players list of friends and get their user details
    def getFriendsList(self, steamid):
        method = '/ISteamUser/GetFriendList/v0001/'
        url = settings.STEAM_ROOT_ENDPOINT + method
        params = {'key': settings.STEAM_API_KEY,
                  'steamid': steamid, 'relationship': 'friend'}
        request = requests.get(url, params)
        response = request.json()
        friendsRes = response['friendslist']
        friendsInfoList = []

        # Iterate through each steamid in friends list and get the user details for that steamid
        for f in friendsRes['friends']:
            friendInfo = self.getUserDetails(f['steamid'])['response']['players']
            print(friendInfo)
            friendsInfoList.append(friendInfo)
            
        print(friendsInfoList)
            
        return friendsInfoList

    # Gets the price of an app with an appid as a parameter
    def priceRequest(self, appid):
        try:
            priceRequest = requests.get(
                "http://store.steampowered.com/api/appdetails/?appids=" + str(appid) + "&format=json")
            priceRequest = priceRequest.json()

            # Check for free values & set to 0, get the price if it isnt 0
            if priceRequest.get(str(appid))['success'] == True:
                if priceRequest.get(str(appid))['data']['is_free'] == True:
                    price = 0
                else:
                    price = priceRequest.get(
                        str(appid))['data']['price_overview']['final']
                    price = float(str(price)[0:-2] + "." + str(price)[-2:])

            else:
                price = None

        except Exception as e:
            price = None
            print("price exception" + str(e))

        return price

    # Gets tag description of a tagid (instead of the tag id, returns the name of the tag)
    # Ex. Category, genre, etc.
    # Steamkit only returns a numerical tag id, not the tag name
    def tag_request(self, appid, tag_type, tag_ids):
        try:
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
                        if (k == 'id' and str(v) == tag):
                            returnList.append(item)

            # Return Fomrat (list of dicts with the id and description):
            # [
            #   {'id': '1', 'description': 'Action'},
            #   {'id': '37', 'description': 'Free to Play'}
            # ]
            #

            return returnList

        except Exception as e:
            print('Oopsies, something went wrong with Tag Request for appid ... ' +
                  str(appid) + ' and error: ' + str(e))
            returnList = None
            return returnList
