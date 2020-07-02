import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

from django.shortcuts import render
from game.models import Game, GameChange, Developer, Publisher, Genre, Languages, AppType
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from game.serializers import GameSerializer, LogSerializer, GameLogSerializer, DeveloperPageSerializer, PublisherPageSerializer, GenrePageSerializer, LanguageSerializer, AppTypeSerializer
from django.utils.timezone import datetime
from game.pagination import StandardResultsSetPagination
from rest_framework import filters
import requests


def index(request):
    games = Game.objects.all()
    changelog = GameChange.objects.all().order_by('-created_time')

    return render(request, 'homepage.html', {'games': games, 'changelog': changelog})


def gameoverview(request, game_appid, game_slug):
    game = get_object_or_404(Game, appid=int(game_appid))

    return render(request, 'gameoverview.html', {'game': game})


# Returns all apps in our DB
# @URL: games/
class GameList(generics.ListAPIView):
    serializer_class = GameSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'appid']
    ordering = ['-id']

    def get_queryset(self):
        queryset = Game.objects.all()
        controllerSupport = self.request.query_params.get('controllerSupport', None)
        if controllerSupport == 'true':
            queryset = queryset.filter(controller_support = 'full')

        releaseState = self.request.query_params.get('releaseState', None)
        if releaseState == 'true':
            queryset = queryset.filter(release_state = 'released')

        isFree = self.request.query_params.get('isFree', None)
        if isFree == 'true':
            queryset = queryset.filter(current_price__price = 0)

        os = self.request.query_params.get('os', None)
        if os == 'Windows':
            queryset = queryset.filter(os__os = 'WIN')
        if os == 'Mac':
            queryset = queryset.filter(os__os = 'MAC')
        if os == 'Linux':
            queryset = queryset.filter(os__os = 'LIN')

        language = self.request.query_params.get('langPayload', None)
        if language is not None and language != '':
            queryset = queryset.filter(supported_languages__language = language)

        appType = self.request.query_params.get('appTypePayload', None)
        if appType is not None and appType != '':
            queryset = queryset.filter(app_type__app_type = appType)

        weebFilter = self.request.query_params.get('weebFilter', None)
        if weebFilter == 'true':
            queryset = queryset.exclude(genres__genre_description = 'Sexual Content')


        return queryset



# Returns a single app from our DB
# @URL: games/<int:appid>
class GameDetail(generics.RetrieveAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    lookup_field = 'appid'


# Returns the 10 most recent changelogs
# @URL: logs/
class LogList(generics.ListAPIView):
    queryset = GameChange.objects.all().order_by('-id')[:10]
    serializer_class = LogSerializer


# Returns all logs (paginated)
# @url: alllogs/
class AllLogs(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['changelog', 'action', 'id', 'game__name', 'game__appid']
    pagination_class = StandardResultsSetPagination
    queryset = GameChange.objects.all()
    serializer_class = LogSerializer

# Returns all Developers
# @url: developers/
class DeveloperList(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['developer']
    pagination_class = StandardResultsSetPagination
    queryset = Developer.objects.all()
    serializer_class = DeveloperPageSerializer

# Returns all Publihers
# @url: publishers/
class PublisherList(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['publisher']
    pagination_class = StandardResultsSetPagination
    queryset = Publisher.objects.all()
    serializer_class = PublisherPageSerializer

# Returns all Genres
# @url: genres/
class GenreList(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['genre_description']
    pagination_class = StandardResultsSetPagination
    queryset = Genre.objects.all()
    serializer_class = GenrePageSerializer

class LanguageList(generics.ListAPIView):
    queryset = Languages.objects.all()
    serializer_class = LanguageSerializer

class AppTypeList(generics.ListAPIView):
    queryset = AppType.objects.all()
    serializer_class = AppTypeSerializer

# Grabs all games via genre
class GamesByGenre(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'appid']
    pagination_class = StandardResultsSetPagination
    serializer_class = GameSerializer

    def get_queryset(self):
        genre_id = self.kwargs['genreid']
        queryset = Game.objects.filter(genres__id = genre_id)
        return queryset

# Grabs all games via Developer
class GamesByDeveloper(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'appid']
    pagination_class = StandardResultsSetPagination
    serializer_class = GameSerializer

    def get_queryset(self):
        developer_id = self.kwargs['developerid']
        queryset = Game.objects.filter(developer__id = developer_id)
        return queryset

# Grabs all games via Publisher
class GamesByPublisher(generics.ListAPIView):
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'appid']
    pagination_class = StandardResultsSetPagination
    serializer_class = GameSerializer

    def get_queryset(self):
        publisher_id = self.kwargs['publisherid']
        queryset = Game.objects.filter(publisher__id = publisher_id)
        return queryset

# Returns custom data about out db
# @response:
#   - appcount: number of apps in our database
#
# @URL: appcount/
class AppCount(APIView):
    def get(self, request):
        data = {}
        numApps = Game.objects.all().count()
        data['appcount'] = str(numApps)

        return Response(data)


# Returns the count of logs registered today
# @URL: logstoday/
class LogsToday(APIView):
    def get(self, request):
        data = {}
        today = datetime.today()
        numLogs = GameChange.objects.filter(created_time__year=today.year,
                                            created_time__month=today.month, created_time__day=today.day).count()
        data['logcount'] = str(numLogs)

        return Response(data)


# Returns changelogs for a given game
# @URL: gamelogs/<int:appid>
class GameLogs(generics.ListAPIView):
    serializer_class = GameLogSerializer

    def get_queryset(self):
        appid = self.kwargs['appid']
        game = Game.objects.filter(appid=appid)
        return GameChange.objects.filter(game__appid=appid)
