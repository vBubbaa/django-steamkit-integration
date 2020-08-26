from django.urls import path, include
from game import views

app_name = 'game'
urlpatterns = [
    path('user/', include('steamapiwrapper.urls')),
    # All Games
    path('games/', views.GameList.as_view()),
    # Singular game instace by appid NOT primary key (db ID)
    path('games/<int:appid>', views.GameDetail.as_view()),
    # 9 most recent games
    path('recentgames/', views.RecentGames.as_view()),
    # 10 most recent change logs
    path('logs/', views.LogList.as_view()),
    path('logstoday/', views.LogsToday.as_view()),
    path('gamelogs/<int:appid>', views.GameLogs.as_view()),
    path('appcount/', views.AppCount.as_view()),
    path('alllogs/', views.AllLogs.as_view()),
    path('developers/', views.DeveloperList.as_view()),
    path('publishers/', views.PublisherList.as_view()),
    path('genres/', views.GenreList.as_view()),
    path('gamesbygenre/<int:genreid>', views.GamesByGenre.as_view()),
    path('gamesbydeveloper/<int:developerid>',
         views.GamesByDeveloper.as_view()),
    path('gamesbypublisher/<int:publisherid>',
         views.GamesByPublisher.as_view()),
    path('languages/', views.LanguageList.as_view()),
    path('apptypes/', views.AppTypeList.as_view()),
    path('steamspy/<int:appid>', views.SteamSpyView.as_view()),
]
