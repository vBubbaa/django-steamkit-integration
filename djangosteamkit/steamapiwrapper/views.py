import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from utils.ModelProcessor import ModelProcessor
from utils.client import SteamWorker
from utils.SteamApiHandler import SteamApi
from django.shortcuts import render
from game.models import Game
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.core.management import call_command
import requests


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
        self.apps = []

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

        worker = SteamWorker()
        worker.login()
        processor = ModelProcessor()
        api = SteamApi()

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
                    'image': 'https://steamcdn-a.akamaihd.net/steam/apps/' + str(dbgame.appid) + '/header.jpg'
                }
                # Append the game to our games list we will pass back
                self.games.append(formatGame)
                print('game exists')
            # If the game does not exist, we will create it using our management create app command,
            # which uses steamkit to create a model object of the app
            else:
                print('game does not exist')
                newGame = processor.processNewGame(game['appid'], 1337, worker, api)  
                formatGame = {
                    'appid': str(newGame.appid),
                    'name': newGame.name,
                    'current_price': str(newGame.current_price.price),
                    'total_playtime': str(round(game['playtime_forever'] / 60, 2)),
                    'image': 'https://steamcdn-a.akamaihd.net/steam/apps/' + str(newGame.appid) + '/header.jpg'
                }
                # Append the game to our games list we will pass back
                self.games.append(formatGame)     

        # Append the game list to the response
        self.res['games'] = self.games

    def get(self, request, *args, **kwargs):
        self.steamid = kwargs.get('steamid')
        self.getGames()
        return Response(self.res)
