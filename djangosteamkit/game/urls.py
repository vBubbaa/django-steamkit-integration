from django.urls import path, include
from game import views

app_name = 'game'
urlpatterns = [
    path('games', views.GameList.as_view())
]
