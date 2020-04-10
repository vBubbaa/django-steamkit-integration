from django.urls import path, include
from steamapiwrapper import views

app_name = 'steamapiwrapper'
urlpatterns = [
    # All Games
    path('useroverview/<int:steamid>', views.UserOverview.as_view()),
]
