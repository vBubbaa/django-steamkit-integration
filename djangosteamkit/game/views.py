from django.shortcuts import render
from game.models import Game, GameChange
from django.shortcuts import get_object_or_404
from rest_framework import generics
from game.serializers import GameSerializer


def index(request):
    games = Game.objects.all()
    changelog = GameChange.objects.all().order_by('-created_time')

    return render(request, 'homepage.html', {'games': games, 'changelog': changelog})


def gameoverview(request, game_appid, game_slug):
    game = get_object_or_404(Game, appid=int(game_appid))

    return render(request, 'gameoverview.html', {'game': game})


class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
