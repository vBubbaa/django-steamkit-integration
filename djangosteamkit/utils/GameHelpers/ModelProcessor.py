from game.models import Game, GameChange, OSOptions, Languages, AppType, Developer, Publisher, Genre, Category, Price
from utils.GameHelpers.Client import Client
from utils.GameHelpers.ApiToolkit import tag_request
from datetime import datetime
from django.utils.timezone import make_aware
from django.utils.text import slugify

import sys


"""
ProcessNewGame() function creates an app based on the Steamkit response (We dont have the app in our DB yet)
@params:
    - client: The steamkit client object we are using to connect to steamkit and perform steamkit actions
    - appid: The appid of the app we are processing
    - changenum: The changenumber of the app we are adding (this is a changenumber given by steamkit)
"""


def ProcessNewGame(client, appid, changenum):
    client = client
    appid = appid
    changenum = changenum

    # Grab the game info from the Client
    gameInfo = client.get_all_product_info(appid)

    # If the gameinfo returned something, set the Game object with the returned attributes
    if gameInfo is not None:
        game = Game(
            appid=appid,
            name=gameInfo['name'],
            slug=gameInfo['slug'],
            release_state=gameInfo['release_state'],
            icon=gameInfo['icon'],
            logo=gameInfo['logo'],
            logo_small=gameInfo['logo_small'],
            clienticon=gameInfo['clienticon'],
            controller_support=gameInfo['controller_support'],
            steam_release_date=epochToDateTime(gameInfo['steam_release_date']),
            metacritic_score=gameInfo['metacritic_score'],
            metacritic_fullurl=gameInfo['metacritic_fullurl'],
            community_visible_stats=boolify(
                gameInfo['community_visible_stats']),
            workshop_visible=boolify(gameInfo['workshop_visible']),
            community_hub_visible=boolify(gameInfo['community_hub_visible']),
            review_score=int(gameInfo['review_score']),
            review_percentage=int(gameInfo['review_percentage'])
        )
        game.save()

        # Generate new price instance and set the recieved price to the apps current price
        price = Price(
            price=gameInfo['price']
        )
        price.save()
        game.prices.add(price)
        game.current_price = price
        game.save()

        # Generate all categories related to the app
        categories = gameInfo['category']
        catList = []
        for cat in categories:
            catList.append(cat.split('_')[1])
        catRes = tag_request(str(appid), 'categories', catList)

        # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
        for item in catRes:
            for k, v in item.items():
                # When the key is ID, check if that genre exists in our genre model
                if (k == 'id'):
                    if Category.objects.filter(category_id=v).exists():
                        category = Category.objects.get(category_id=v)
                        # If exists, associate the game to that genre
                        game.categories.add(category)
                    else:
                        # If the genre doesn't exist in our genre model, create it
                        category = Category.objects.create(category_id=v)
                elif (k == 'description'):
                    # If the desciption for the genre is not yet set, set it and associate game with the genre
                    if not category.category_description:
                        print('genre v ' + v)
                        category.category_description = v
                        category.save()
                        game.categories.add(category)

                game.save()

        # Generate all genres related to the app
        tags = gameInfo['genres']
        tagList = []
        for tag in tags.items():
            tagList.append(tag[1])
        tagRes = tag_request(str(appid), 'genres', tagList)

        # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
        for item in tagRes:
            for k, v in item.items():
                # When the key is ID, check if that genre exists in our genre model
                if (k == 'id'):
                    if Genre.objects.filter(genre_id=v).exists():
                        genre = Genre.objects.get(genre_id=v)
                        # If exists, associate the game to that genre
                        game.genres.add(genre)
                    else:
                        # If the genre doesn't exist in our genre model, create it
                        genre = Genre.objects.create(genre_id=v)
                elif (k == 'description'):
                    # If the desciption for the genre is not yet set, set it and associate game with the genre
                    if not genre.genre_description:
                        print('genre v ' + v)
                        genre.genre_description = v
                        genre.save()
                        game.genres.add(genre)

                game.save()

        # Generate primary genre
        pg = gameInfo['primary_genre']
        tagList = []
        tagList.append(pg)
        # Send the list of tag ids we need to our function that fetches the tag description via steamAPI
        tagRes = tag_request(str(appid), 'genres', tagList)

        # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
        for item in tagRes:
            for k, v in item.items():
                # When the key is ID, check if that genre exists in our genre model
                if (k == 'id'):
                    if Genre.objects.filter(genre_id=v).exists():
                        genre = Genre.objects.get(genre_id=v)
                        # If exists, set the primary genre to that genre
                        game.primary_genre = genre
                    else:
                        # If the genre doesn't exist in our genre model, create it
                        genre = Genre.objects.create(genre_id=v)
                elif (k == 'description'):
                    # If the desciption for the genre is not yet set, set it and associate game with the primary genre
                    if not genre.genre_description:
                        genre.genre_description = v
                        genre.save()
                        game.primary_genre = genre

                game.save()

        # Language Stuff
        languagesRes = gameInfo['languages']
        if languagesRes is not None:
            for lang in languagesRes.keys():
                print(str(lang))
                langGet = Languages.objects.get_or_create(
                    language=str(lang))[0]
                game.supported_languages.add(langGet)
            game.save()

        appType = gameInfo['app_type']
        if appType is not None:
            typeGetOrCreate = AppType.objects.get_or_create(app_type=appType)[
                0]
            game.app_type.add(typeGetOrCreate)
            game.save()

        # OS list Stuff
        oslist = gameInfo['oslist']
        print('OSLIST@@@@@@@@@@@@@@@@@@@@@@@ ' + str(oslist))
        if oslist is not None:
            # If there is an OSList, split the list by ',' delimiter
            oslist = gameInfo['oslist'].split(',')
            # For each of those OS', check for their type and add them to the model
            for os in oslist:
                print(
                    "################## OS #######################")
                print(os)
                if (os == 'windows'):
                    game.os.add(
                        OSOptions.objects.get(os=OSOptions.WIN))
                elif (os == 'macos'):
                    game.os.add(
                        OSOptions.objects.get(os=OSOptions.MAC))
                else:
                    game.os.add(
                        OSOptions.objects.get(os=OSOptions.LIN))
            game.save()

        # Associations (publishers and developers for a given game)
        assoc = gameInfo['associations']
        print('associations')
        if assoc is not None:
            # Loop through each association  through .values()
            for a in assoc.values():
                # If type is developer, either get the existing developer from our model or create one and associate it with our game
                if a['type'] == 'developer':
                    devGetOrCreate = Developer.objects.get_or_create(
                        developer=a['name'])[0]
                    game.developer.add(devGetOrCreate)
                # If type is publisher, either get the existing publisher from our model or create one and associate it with our game
                else:
                    pubGetOrCreate = Publisher.objects.get_or_create(
                        publisher=a['name'])[0]
                    game.publisher.add(pubGetOrCreate)
            game.save()

        # Change number stuff
        # Register the change that occured in the changelog model
        gamechange = GameChange(
            change_number=changenum,
            game=game,
            changelog=GameChange.changelog_builder(
                GameChange.ADD,
                game.appid,
            ),
            action=GameChange.ADD
        )
        gamechange.save()

        print("Change Number " +
              str(gamechange.change_number) + ' registered.')
    else:
        print(
            '######### no common section, continue on #########')


"""
ProcessExistingGame() is called on an app when a change is read through steamkit and the appid already
exists in our DB

@params:
    - client: The client instance we are connected to steamkit with
    - appid: The appid of the app we need to check for changes
"""


def ProcessExistingGame(client, appid, changenum):
    client = client
    appid = appid
    changenum = changenum

    # Grab the game info from the Client
    gameInfo = client.get_all_product_info(appid)

    # Grab the game object we are checking for changes on
    game = Game.objects.get(appid=appid)

    # Fields we can check by simply comparing strings (ex. NOT fields with relationships [fk, m2m])
    easyFieldChecks = [
        'name', 'release_state', 'icon', 'logo', 'logo_small', 'clienticon', 'controller_support'
    ]

    # For each easily checkable field, run compareCharField()
    for field in easyFieldChecks:
        if gameInfo[field] is not None:
            compareCharField(
                getattr(game, field),
                gameInfo[field],
                game,
                field,
                changenum
            )
        else:
            pass

    if gameInfo['price'] != game.current_price.price:
        price = Price(
            price=gameInfo['price']
        )
        price.save()
        game.prices.add(price)
        game.current_price = price
        game.save()


""" 
Compares two charfields and checks if there is a difference (used to check game fields that aren't tied with fk's or m2m relationships)
@params:
    - currentVal: Current val stored in db
    - steamkitVal: Value returned from steamkit (current)
    - game: game object which we are checking
    - db_field_name: field of the object we are checking (ex. name, releasestate, etc.)
    - changenum: the changenumber we are working on (returned from steamkit)
"""


def compareCharField(currentVal, steamkitVal, game, db_field_name, changenum):
    # If the chars are equal, no change has happened so return None
    if str(currentVal) == str(steamkitVal):
        print('No change for field: ' + db_field_name)
        pass
    # Else, a change did occur for a field so return the new val so we can set it in our DB
    else:
        setattr(game, db_field_name, steamkitVal)
        # If the name field changed, we also need to reslug our object to reflect the new name
        if db_field_name == 'name':
            game.slug = slugify(steamkitVal, allow_unicode=True)
        game.save()

        payload = str(db_field_name) + ' updated: ' + \
            str(currentVal) + ' => ' + str(steamkitVal)
        gameChange = GameChange(
            change_number=changenum,
            game=game,
            changelog=GameChange.changelog_builder(
                GameChange.UPDATE,
                game.appid,
                payload=payload
            ),
            action=GameChange.UPDATE
        )
        gameChange.save()

# Steam bool res fields return a string of 1 or 0, so this just returns a boolean representation of that


def boolify(num):
    if num == '1':
        return True
    else:
        return False

# Release dates are returned as epochs, so this converts it to a django friendly datetime format


def epochToDateTime(timestamp):
    if timestamp is not None:
        return make_aware(datetime.fromtimestamp(int(timestamp)))
    else:
        return None
