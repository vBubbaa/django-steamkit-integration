from django.db import models
from django.utils import timezone


class Game(models.Model):
    appid = models.IntegerField()
    name = models.CharField(max_length=264)
    slug = models.SlugField()
    # Get price from API (apitoolkit.py)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    os = models.ManyToManyField('OSOptions')
    release_state = models.CharField(max_length=32, null=True)
    icon = models.CharField(max_length=128, null=True)
    logo = models.CharField(max_length=128, null=True)
    logo_small = models.CharField(max_length=128, null=True)
    clienticon = models.CharField(max_length=128, null=True)
    supported_languages = models.ManyToManyField('Languages')
    app_type = models.ManyToManyField('AppType')
    controller_support = models.CharField(max_length=32, null=True, blank=True)
    developer = models.ManyToManyField('Developer')
    publisher = models.ManyToManyField('Publisher')
    primary_genre = models.ForeignKey(
        'Genre', on_delete=models.CASCADE, related_name='primary_genre', blank=True, null=True)
    genres = models.ManyToManyField('Genre')
    categories = models.ManyToManyField('Category')

    def __str__(self):
        return self.name

    # Build the url to the given picture val (icon, logo, logo_small, clienticon)
    def pictureUrlBuilder(self, val):
        return 'https://steamcdn-a.akamaihd.net/steamcommunity/public/images/apps/' + self.appid + '/ ' + val + '.jpg'


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


class Languages(models.Model):
    language = models.CharField(max_length=128)

    def __str__(self):
        return self.language


class AppType(models.Model):
    app_type = models.CharField(max_length=32)

    def __str__(self):
        return self.app_type


class Developer(models.Model):
    developer = models.CharField(max_length=128)

    def __str__(self):
        return self.developer


class Publisher(models.Model):
    publisher = models.CharField(max_length=128)

    def __str__(self):
        return self.publisher


class Genre(models.Model):
    genre_id = models.IntegerField()
    genre_description = models.CharField(max_length=128)

    def __str__(self):
        return self.genre_description


class Category(models.Model):
    category_id = models.IntegerField()
    category_description = models.CharField(max_length=128)

    def __str__(self):
        return self.category_description
