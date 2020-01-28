from django.shortcuts import render
from game.models import Game, GameChange
from django.shortcuts import get_object_or_404

def index(request):
    games = Game.objects.all()
    return render(request, 'homepage.html', {'games': games})

def gameoverview(request, game_appid, game_slug):
    game = get_object_or_404(Game, appid=int(game_appid))

    return render(request, 'gameoverview.html', {'game':game})
