import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from django.conf import settings
import requests

# Threading for faster response building
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
from django.conf import settings

class SteamApi():
    def __init__(self):
        self.key = '?key=' + settings.STEAM_API_KEY
        self.baseurl = 'http://api.steampowered.com'
        self.format = '&format=json'

    def getUserLibrary(self, steamid):
        method = '/IPlayerService/GetOwnedGames/v0001/'
        url = self.baseurl + method + self.key + \
            '&steamid=' + str(steamid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    def getAppDetails(self, appid):
        method = '/appdetails/'
        url = 'https://store.steampowered.com/api/appdetails/' + \
            self.key + '&appids=' + str(appid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    def getVacInfo(self, steamid):
        method = '/ISteamUser/GetPlayerBans/v1/'
        url = self.baseurl + method + self.key + \
            '&steamids=' + str(steamid) + self.format
        req = requests.get(url)
        res = req.json()
        return res

    # Gets a players profile details (personaname, picture, etc.)
    def getUserDetails(self, steamid):
        method = '/ISteamUser/GetPlayerSummaries/v001/'
        url = self.baseurl + method + self.key + \
            '&steamids=' + str(steamid) + self.format
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

        # Thread to append friend to a friend list to be returned
        def threadFriends(f):
            friendInfo = self.getUserDetails(
                f['steamid'])['response']['players']
            friendsInfoList.append(friendInfo)

        # Excute friend loop with threading to speed up the requests
        with ThreadPoolExecutor(max_workers=8) as executor:
            if bool(friendsRes['friends']):
                for f in friendsRes['friends']:
                    executor.submit(threadFriends, f)

        
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
    def tag_request(self, appid, tag_type):
        try:
            # Initial request and response
            tagRequest = requests.get(
                "http://store.steampowered.com/api/appdetails/?appids=" + appid + "&format=json")
            tagRequest = tagRequest.json()
            # Grab the tag type we are fetching (ex. genre, category)
            request = tagRequest.get(appid)['data'][tag_type]

            # Return Fomrat (list of dicts with the id and description):
            # [
            #   {'id': '1', 'description': 'Action'},
            #   {'id': '37', 'description': 'Free to Play'}
            # ]
            #

            return request

        except Exception as e:
            print('Oopsies, something went wrong with Tag Request for appid ... ' +
                  str(appid) + ' and error: ' + str(e))
            returnList = None
            return returnList
