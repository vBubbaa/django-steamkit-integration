from django.shortcuts import render
from game.models import Game, GameChange

def index(request):
    return render(request, 'homepage.html')
