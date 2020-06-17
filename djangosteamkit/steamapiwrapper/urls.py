from django.urls import path, include
from steamapiwrapper import views

app_name = 'steamapiwrapper'
urlpatterns = [
    # All Games
    path('useroverview/<int:steamid>', views.UserOverview.as_view()),
    path('friendselect/<int:steamid>', views.GetFriendList.as_view()),
    path('compare/', views.GetComparedGames.as_view())
]
