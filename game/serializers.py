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
        fields = '__all__'


class PublisherSerializer(ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


# Only get the description, however we can also get the ID Steam associates with this tag by calling 'genre_id'
class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


# Only get the description, however we can also get the ID Steam associates with this tag by calling 'category_id'
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


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
    # Date field format
    steam_release_date = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = Game
        fields = '__all__'


class GameNameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = ['name', 'appid', 'slug']


class DeveloperPageSerializer(ModelSerializer):
    # Method to get game count of developer
    game_count = serializers.SerializerMethodField()

    class Meta:
        model = Developer
        fields = '__all__'

    def get_game_count(self, developer):
        return Game.objects.filter(developer=developer).count()


class PublisherPageSerializer(ModelSerializer):
    # Method to get game count of developer
    game_count = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = '__all__'

    def get_game_count(self, publisher):
        return Game.objects.filter(publisher=publisher).count()


class GenrePageSerializer(ModelSerializer):
    # Method to get game count of developer
    game_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = '__all__'

    def get_game_count(self, genres):
        return Game.objects.filter(genres=genres).count()


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
