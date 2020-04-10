from django.shortcuts import render
from game.models import Game
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
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
                    'total_playtime': str(round(game['playtime_forever'] / 60, 2))
                }
                # Append the game to our games list we will pass back
                self.games.append(formatGame)
                print('game exists')
            # If the game does not exist, we will create it using our management create app command,
            # which uses steamkit to create a model object of the app
            else:
                print('game does not exist')

        # Append the game list to the response
        self.res['games'] = self.games

    def get(self, request, *args, **kwargs):
        self.steamid = kwargs.get('steamid')
        self.getGames()
        return Response(self.res)
