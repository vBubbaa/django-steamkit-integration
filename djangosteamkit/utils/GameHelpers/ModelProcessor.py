from game.models import Game, GameChange, OSOptions, Languages, AppType
from utils.GameHelpers.Client import Client


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
            clienticon=gameInfo['clienticon']
        )
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
