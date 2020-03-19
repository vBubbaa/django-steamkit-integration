from django.shortcuts import render
from game.models import Game, GameChange
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from game.serializers import GameSerializer, LogSerializer
from django.utils.timezone import datetime
import requests


def index(request):
    games = Game.objects.all()
    changelog = GameChange.objects.all().order_by('-created_time')

    return render(request, 'homepage.html', {'games': games, 'changelog': changelog})


def gameoverview(request, game_appid, game_slug):
    game = get_object_or_404(Game, appid=int(game_appid))

    return render(request, 'gameoverview.html', {'game': game})


# Returns all apps in our DB
class GameList(generics.ListAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer


# Returns a single app from our DB
class GameDetail(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'appid'


# Returns the 10 most recent changelogs
class LogList(generics.ListAPIView):
    queryset = GameChange.objects.all().order_by('-id')[:10]
    serializer_class = LogSerializer


# Returns custom data about out db
# @response:
#   - appcount: number of apps in our database
#
class AppCount(APIView):
    def get(self, request):
        data = {}
        numApps = Game.objects.all().count()
        data['appcount'] = str(numApps)

        return Response(data)


# Returns the count of logs registered today
class LogsToday(APIView):
    def get(self, request):
        data = {}
        today = datetime.today()
        numLogs = GameChange.objects.filter(created_time__year=today.year,
                                            created_time__month=today.month, created_time__day=today.day).count()
        data['logcount'] = str(numLogs)

        return Response(data)
