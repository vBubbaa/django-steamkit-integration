from django.contrib import admin
from game.models import Game, GameChange, OSOptions, Languages, AppType, Developer, Publisher, Genre, Category

admin.site.register(Game)
admin.site.register(GameChange)
admin.site.register(OSOptions)
admin.site.register(Languages)
admin.site.register(AppType)
admin.site.register(Developer)
admin.site.register(Publisher)
admin.site.register(Genre)
admin.site.register(Category)
