from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from game.models import Game, Price, OSOptions, Languages, AppType, Developer, Publisher, Genre, Category, GameChange


# M2M and FK relation serializers so we can pull the value and not the ID #
class PriceSerializer(ModelSerializer):
    class Meta:
        model = Price
        fields = ['price', 'date']


class OSOptionsSerializer(ModelSerializer):
    class Meta:
        model = OSOptions
        fields = ['os']


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = Languages
        fields = ['language']


class AppTypeSerializer(ModelSerializer):
    class Meta:
        model = AppType
        fields = ['app_type']


class DeveloperSerializer(ModelSerializer):
    class Meta:
        model = Developer
        fields = ['developer']


class PublisherSerializer(ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['publisher']


# Only get the description, however we can also get the ID Steam associates with this tag by calling 'genre_id'
class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ['genre_description']


# Only get the description, however we can also get the ID Steam associates with this tag by calling 'category_id'
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_description']


#   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #


# Serialize all games in the DB
class GameSerializer(ModelSerializer):
    # The relation fields (m2m, f2k) with custom serializers to pull the correct values
    prices = PriceSerializer(many=True)
    current_price = PriceSerializer()
    os = OSOptionsSerializer(many=True)
    supported_languages = LanguageSerializer(many=True)
    app_type = AppTypeSerializer()
    developer = DeveloperSerializer(many=True)
    publisher = PublisherSerializer(many=True)
    genres = GenreSerializer(many=True)
    primary_genre = GenreSerializer()
    categories = CategorySerializer(many=True)
    #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #   #

    class Meta:
        model = Game
        fields = '__all__'


class GameNameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ['name']


class LogSerializer(ModelSerializer):
    game = GameNameSerializer()
    created_time = serializers.DateTimeField(source='format_date')

    class Meta:
        model = GameChange
        fields = '__all__'


class GameLogSerializer(ModelSerializer):
    game = GameNameSerializer()
    created_time = serializers.DateTimeField(source='format_date')

    class Meta:
        model = GameChange
        fields = '__all__'
