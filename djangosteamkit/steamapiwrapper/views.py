from collections import Counter
import requests
from django.core.management import call_command
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from game.models import Game
from django.shortcuts import render
from utils.SteamApiHandler import SteamApi
from utils.client import SteamWorker
from utils.ModelProcessor import ModelProcessor
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()


# Endpoint route: userapi/useroverview/<int:steamid>


class UserOverview(APIView):
    def __init__(self):
        # Steam web api method of to grab owned games by player
        self.method = '/IPlayerService/GetOwnedGames/v001'
        # Passed back res with all games parsed with correct information from out database
        self.res = {}
        # Steamid we will set by the URL parameter @steamid
        self.steamid = None
        self.games = []
        self.vacInfo = []
        self.userDetails = []
        self.libraryCost = 0

        self.worker = SteamWorker()
        self.worker.login()
        self.processor = ModelProcessor()
        self.api = SteamApi()

    # Func to get games from request, then get the additional game information from our database
    # Will return a json object with:
    #   - Total game count
    #   - A list of games: (Game Name, Appid, Current Price)
    # This parsed response will be pass back to the enpoint request /userapi/useroverview/<int:steamid>
    def getGames(self):
        url = settings.STEAM_ROOT_ENDPOINT + self.method
        params = {'key': settings.STEAM_API_KEY, 'steamid': self.steamid}
        request = requests.get(url, params)
        response = request.json()
        self.res['game_count'] = response['response']['game_count']
        games = response['response']['games']

        for game in games:
            # Check if game exists in our database
            if Game.objects.filter(appid=game['appid']).exists():
                # Get the game
                dbgame = Game.objects.get(appid=game['appid'])
                # Grab the information of the game that we need and format it into an object
                print(dbgame.appid)
                formatGame = {
                    'appid': str(dbgame.appid),
                    'name': dbgame.name,
                    'current_price': str(dbgame.current_price.price),
                    'total_playtime': str(round(game['playtime_forever'] / 60, 2)),
                    'image': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/' + str(dbgame.appid) + '/' + str(dbgame.logo) + '.jpg'
                }
                # Append the game to our games list we will pass back
                self.games.append(formatGame)
                print('game exists')
            # If the game does not exist, we will create it using our management create app command,
            # which uses steamkit to create a model object of the app
            else:
                print('game does not exist')
                newGame = self.processor.processNewGame(
                    game['appid'], 1337, self.worker, self.api)
                # processor.processNewGame(appid, changenum, worker, api)
                formatGame = {
                    'appid': str(newGame.appid),
                    'name': newGame.name,
                    'current_price': str(newGame.current_price.price),
                    'total_playtime': str(round(game['playtime_forever'] / 60, 2)),
                    'image': 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/' + str(newGame.appid) + '/' + str(newgame.logo) + '.jpg'
                }
                # Append the game to our games list we will pass back
                self.games.append(formatGame)

            if formatGame['current_price'] is not None:
                self.libraryCost += float(formatGame['current_price'])

        # Append the game list to the response
        self.res['games'] = self.games
        self.res['libcost'] = self.libraryCost

    def getVacs(self):
        vacs = self.api.getVacInfo(self.steamid)
        self.res['vacinfo'] = vacs

    def getUserDetails(self):
        userDetails = self.api.getUserDetails(self.steamid)
        print(userDetails)
        self.res['userdetails'] = userDetails

    def get(self, request, *args, **kwargs):
        self.steamid = kwargs.get('steamid')
        self.getGames()
        self.getVacs()
        self.getUserDetails()
        print(self.res)
        return Response(self.res)


class GetFriendList(APIView):
    def __init__(self):
        self.method = '/ISteamUser/GetFriendList/v0001/'
        # Steamid we will set by the URL parameter @steamid
        self.steamid = None
        self.res = {}
        self.api = SteamApi()

    def getGames(self):
        friends = self.api.getFriendsList(self.steamid)
        self.res['friends'] = friends

    def get(self, request, *args, **kwargs):
        self.steamid = kwargs.get('steamid')
        self.getGames()
        return Response(self.res)


class GetComparedGames(APIView):
    def __init__(self):
        self.sids = []
        self.gameList = []
        self.commonGames = []

        self.worker = SteamWorker()
        self.worker.login()
        self.processor = ModelProcessor()
        self.api = SteamApi()

    def getGames(self):
        return None

    # Processes the SID parameters so we can get a compared list going
    def processIdParams(self, sids):
        for k, v in sids.items():
            print('SID: ' + v)
            self.sids.append(v)
        return self.sids

    def getCommonGames(self):
        # Loop through each comparee
        for sid in self.sids:
            # Get their game app library
            userLib = self.api.getUserLibrary(sid)
            # Loop through each game and append it to the game list
            for game in userLib['response']['games']:
                self.gameList.append(game['appid'])

        # https://stackoverflow.com/a/15812667
        # stores all common appids in var 'out'
        counter = Counter(self.gameList)
        out = [value for value, count in counter.items() if count > 1]

        # Get each game from commongames from db or create it
        for game in out:
            if Game.objects.filter(appid=game).exists():
                dbgame = Game.objects.get(appid=game)
                formatGame = {
                    'appid': str(dbgame.appid),
                    'name': dbgame.name,
                    'current_price': str(dbgame.current_price.price),
                    'image': 'https://steamcdn-a.akamaihd.net/steam/apps/' + str(dbgame.appid) + '/header.jpg',
                    'slug': str(dbgame.slug)
                }
                self.commonGames.append(formatGame)
            else:
                newGame = self.processor.processNewGame(
                    game, 1337, self.worker, self.api)
                # processor.processNewGame(appid, changenum, worker, api)
                formatGame = {
                    'appid': str(newGame.appid),
                    'name': newGame.name,
                    'current_price': str(newGame.current_price.price),
                    'image': 'https://steamcdn-a.akamaihd.net/steam/apps/' + str(newGame.appid) + '/header.jpg',
                    'slug': str(newGame.slug)
                }
                # Append the game to our games list we will pass back
                self.commonGames.append(formatGame)

    def get(self, request, *args, **kwargs):
        self.processIdParams(request.query_params)
        self.getCommonGames()
        return Response(self.commonGames)
