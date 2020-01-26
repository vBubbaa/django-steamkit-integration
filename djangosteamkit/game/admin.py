from django.contrib import admin
from .models import Game, GameChange, OSOptions

admin.site.register(Game)
admin.site.register(GameChange)
admin.site.register(OSOptions)
