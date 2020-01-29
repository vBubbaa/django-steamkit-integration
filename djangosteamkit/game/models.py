from django.db import models
from django.utils import timezone

class Game(models.Model):
    appid = models.IntegerField()
    name = models.CharField(max_length=264)
    slug = models.SlugField()
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    os = models.ManyToManyField('OSOptions')
    release_state = models.CharField(max_length=32, null=True)
    icon = models.CharField(max_length=128, null=True)
    logo = models.CharField(max_length=128, null=True)
    logo_small = models.CharField(max_length=128, null=True)
    clienticon = models.CharField(max_length=128, null=True)
    clienttga = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.name

class GameChange(models.Model):
    # Action constants
    ADD = 'ADD'
    UPDATE = 'UPDATE'

    change_number = models.IntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, default=None)
    created_time = models.DateTimeField(default=timezone.now)
    changelog = models.CharField(max_length=264, default=None)
    action = models.CharField(max_length=8, null=True)

    def __str__(self):
        return self.changelog

    def changelog_builder(action, appid, payload=None):
        if payload:
            changelog = str(action) + ' ' + str(appid) + ': ' + str(payload)
        else:
            changelog = str(action) + ' ' + str(appid) + ' to the database'
        return changelog



class OSOptions(models.Model):
    # OS Constants
    WIN = 'WIN'
    MAC = 'MAC'
    LIN = 'LIN'

    # Choices for OS
    OS_CHOICES = [
        (WIN, 'Windows'),
        (MAC, 'MacOS'),
        (LIN, 'Linux')
    ]

    os = models.CharField(max_length=10, choices=OS_CHOICES)

    def __str__(self):
        return self.os
