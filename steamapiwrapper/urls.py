from django.urls import path, include
from steamapiwrapper import views

app_name = 'steamapiwrapper'
urlpatterns = [
    # All Games
    path('useroverview/<int:steamid>/', views.UserOverview.as_view()),
    path('useroverview/<int:steamid>/games/',
         views.UserOverviewGames.as_view()),
    path('usersearch/', views.UserSearch.as_view()),
    path('friendselect/<int:steamid>/', views.GetFriendList.as_view()),
    path('friendlocation/<int:steamid>/', views.LocationBuilder.as_view()),
    path('compare/', views.GetComparedGames.as_view()),
]
