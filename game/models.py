from django.db import models
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime


class Game(models.Model):
    appid = models.IntegerField()
    name = models.CharField(max_length=264)
    slug = models.SlugField()
    # All price changes are stored in 'Price' model so we can view the price history
    prices = models.ManyToManyField('Price')
    # The current price of the app
    current_price = models.ForeignKey(
        'Price', on_delete=models.CASCADE, related_name='current_price', blank=True, null=True)
    # Supported OS' [choose from 'windows', 'macos', and 'linux']
    os = models.ManyToManyField('OSOptions')
    # Release state of the game (ex. released, pre-release, etc.)
    release_state = models.CharField(max_length=32, null=True, blank=True)
    # Image stuff that points to the image url on steams domain
    icon = models.CharField(max_length=128, null=True, blank=True)
    logo = models.CharField(max_length=128, null=True, blank=True)
    logo_small = models.CharField(max_length=128, null=True, blank=True)
    clienticon = models.CharField(max_length=128, null=True, blank=True)
    # Languages supported by the app
    supported_languages = models.ManyToManyField('Languages')
    # Type of app (game, dlc, etc.)
    app_type = models.ForeignKey(
        'AppType', on_delete=models.CASCADE, related_name='type', blank=True, null=True)
    # Does the game support controllers? (full, partial, etc)
    controller_support = models.CharField(max_length=32, null=True, blank=True)
    # Developer and publishers (if applicable)
    developer = models.ManyToManyField('Developer')
    publisher = models.ManyToManyField('Publisher')
    # Main genre for the app
    primary_genre = models.ForeignKey(
        'Genre', on_delete=models.CASCADE, related_name='primary_genre', blank=True, null=True)
    # All genre relating to the app
    genres = models.ManyToManyField('Genre', related_name='genres')
    # Categories relating to the app
    categories = models.ManyToManyField('Category')
    # Release date converted from epoch to django datetimefield format
    steam_release_date = models.DateTimeField(null=True, blank=True)
    # Metacritic stuff
    metacritic_score = models.CharField(max_length=264, null=True, blank=True)
    metacritic_fullurl = models.URLField(null=True, blank=True)
    # Other T/F fields
    community_visible_stats = models.BooleanField(
        default=False, null=True, blank=True)
    workshop_visible = models.BooleanField(
        default=False, null=True, blank=True)
    community_hub_visible = models.BooleanField(
        default=False, null=True, blank=True)
    # Review stuff
    review_score = models.IntegerField(null=True, blank=True)
    review_percentage = models.IntegerField(null=True, blank=True)

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

    def format_date(self):
        return naturaltime(self.created_time)


class Price(models.Model):
    price = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.price)


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
