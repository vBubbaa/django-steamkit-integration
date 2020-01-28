from django.urls import path, include
from game import views

app_name = 'game'
urlpatterns = [
    path('', views.index, name='index'),
    path('game/<int:game_appid>/<str:game_slug>/', views.gameoverview, name = 'gameoverview'),
]
