from django.db import models
from django.utils import timezone

class Game(models.Model):
    appid = models.IntegerField()
    name = models.CharField(max_length=264)
    slug = models.SlugField()
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name

class GameChange(models.Model):
    change_id = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, default=None)
    created_time = models.DateTimeField(default=timezone.now)
    changelog = models.CharField(max_length=264, default=None)

    def __str__(self):
        return self.changelog
