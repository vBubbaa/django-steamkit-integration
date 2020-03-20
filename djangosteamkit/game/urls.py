from django.urls import path, include
from game import views

app_name = 'game'
urlpatterns = [
    # All Games
    path('games/', views.GameList.as_view()),
    # Singular game instace by appid NOT primary key (db ID)
    path('games/<int:appid>', views.GameDetail.as_view()),
    path('logs/', views.LogList.as_view()),
    path('logstoday/', views.LogsToday.as_view()),
    path('gamelogs/<int:appid>', views.GameLogs.as_view()),
    path('appcount/', views.AppCount.as_view()),
]
