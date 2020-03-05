from game.models import Game, GameChange, OSOptions, Languages, AppType, Developer, Publisher, Genre, Category
from utils.GameHelpers.Client import Client
from utils.GameHelpers.ApiToolkit import tag_request
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
            price=gameInfo['price'],
            release_state=gameInfo['releasestate'],
            icon=gameInfo['icon'],
            logo=gameInfo['logo'],
            logo_small=gameInfo['logo_small'],
            clienticon=gameInfo['clienticon'],
            controller_support=gameInfo['controller_support'],
        )
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
                        # If exists, set the primary genre to that genre
                        game.primary_genre = Genre.objects.filter(genre_id=v)
                    else:
                        # If the genre doesn't exist in our genre model, create it
                        genre = Genre.objects.create(genre_id=v)
                elif (k == 'description'):
                    # If the desciption for the genre is not yet set, set it and associate game with the primary genre
                    if not genre.genre_description:
                        print('genre v ' + v)
                        genre.genre_description = v
                        genre.save()
                        game.primary_genre = genre

                game.save()

        sys.exit("Exit after genre")

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


def ProcessExistingGame(client, appid):
    client = client
    appid = appid
