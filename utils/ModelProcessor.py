from game.models import Game, Price, Category, Genre, Languages, AppType, OSOptions, Developer, Publisher, GameChange
from django.utils.text import slugify
from datetime import datetime
from django.utils.timezone import make_aware
from time import sleep
import json


class ModelProcessor():
    def __init__(self):
        self.exists = False
        self.changenum = None

    ##############################################################
    # Process a new app in our db with steakit
    # @PARAMS:
    # - appid: appid of app to be added to BD
    # - worker: steamkit worker to handle steamkit calls
    # - api: SteamApi custom object to handle our steam api calls
    ##############################################################
    def processNewGame(self, appid, changenum, worker, api):
        print('Start processing new game')

        # Get the response from steamkit
        # The request for all of the app data via steamkit
        # try:
        req = worker.get_product_info(appids=[appid])

        # Set changenumber
        self.changenum = changenum

        try:
            # Some games get added with no info, so just add it to the db with the appid
            if 'common' not in req['apps'][0]['appinfo']:
                print('no common section' + str(req))
                game = Game(
                    appid=appid
                )
        except:
            print('Request is empty "ERROR" no ["apps"], ["0"], ["appinfo"]')

        # Else, the game has information in common section
        else:
            # New Game Declaration for non relationship fields and non-multiple fields
            game = Game(
                appid=appid,
                name=req['apps'][0]['appinfo']['common']['name'],
                slug=slugify(req['apps'][0]['appinfo']['common']
                             ['name'], allow_unicode=True),
                release_state=req['apps'][0]['appinfo']['common'].get(
                    'releasestate', None),
                icon=req['apps'][0]['appinfo']['common'].get('icon', None),
                logo=req['apps'][0]['appinfo']['common'].get('logo', None),
                logo_small=req['apps'][0]['appinfo']['common'].get(
                    'logo_small', None),
                clienticon=req['apps'][0]['appinfo']['common'].get(
                    'clienticon', None),
                controller_support=req['apps'][0]['appinfo']['common'].get(
                    'controller_support', None),
                steam_release_date=self.epochToDateTime(
                    req['apps'][0]['appinfo']['common'].get(
                        'steam_release_date')),
                metacritic_score=req['apps'][0]['appinfo']['common'].get(
                    'metacritic_score', None),
                metacritic_fullurl=req['apps'][0]['appinfo']['common'].get(
                    'metacritic_fullurl', None),
            )

            game.save()

            # Boolean field creation in DB
            self.processBoolFields(req, game)
            # Int field creation in DB
            self.processIntFields(req, game)
            # Add price from steamAPI
            self.addPrice(game, api.priceRequest(game.appid))
            # Add categories
            self.processCategories(req, game, api)
            # Add genres
            self.processGenres(req, game, api)
            # Add primary genre
            self.processPrimaryGenre(req, game, api)
            # Add languages
            self.processLanguages(req, game)
            # Add app type
            self.processAppType(req, game)
            # Add OS options
            self.processOsOptions(req, game)
            # Add Associations (dev, publisher)
            self.processAssociations(req, game)

            # Add changelog for app creation
            gamechange = GameChange(
                change_number=self.changenum,
                game=game,
                changelog=GameChange.changelog_builder(
                    GameChange.ADD,
                    game.appid,
                ),
                action=GameChange.ADD
            )
            gamechange.save()

            # Return the game after the app has been created in the DB
            return game

        # except:
        #     print('Error fetching data from steamkit for app: ' + str(appid))

    # Create boolean fields for new game
    def processBoolFields(self, req, game):
        # Default boolean fields we record for each app (if available)
        DEFAULT_BOOLS = ['community_visible_stats',
                         'workshop_visible', 'community_hub_visible']

        # Loop through each possible boolean and add it to the game object in our db
        for boolean in DEFAULT_BOOLS:
            if(req['apps'][0]['appinfo']['common'].get(boolean)):
                setattr(game, boolean, self.boolify(
                    req['apps'][0]['appinfo']['common'].get(boolean)))
            else:
                setattr(game, boolean, None)
                print(boolean + ' is not available in response')

        game.save()

    # Create int fields for new game
    def processIntFields(self, req, game):
        # Default boolean fields we record for each app (if available)
        DEFAULT_INTS = ['review_score', 'review_percentage']

        # Loop through each possible boolean and add it to the game object in our db
        for integer in DEFAULT_INTS:
            if(req['apps'][0]['appinfo']['common'].get(integer)):
                setattr(game, integer, int(
                    req['apps'][0]['appinfo']['common'].get(integer)))
                print('added int val to db')
            else:
                setattr(game, integer, None)
                print(integer + ' is not available in response')

        game.save()

    # Add price to the app
    def addPrice(self, game, price):
        newPriceObj = Price(price=price)
        newPriceObj.save()
        game.prices.add(newPriceObj)
        game.current_price = newPriceObj
        game.save()

    # Generate all categories realted to the app
    def processCategories(self, req, game, api):
        categories = req['apps'][0]['appinfo']['common'].get(
            'category', None)
        if categories is not None:
            catList = []
            for cat in categories:
                catList.append(cat.split('_')[1])
            # Get string value of tag from tag ID via SteamAPI() > fnc(tag_request)
            catRes = api.tag_request(str(game.appid), 'categories', catList)
            if catRes is not None:
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
                                category = Category.objects.create(
                                    category_id=v)
                        elif (k == 'description'):
                            # If the desciption for the genre is not yet set, set it and associate game with the genre
                            if not category.category_description:
                                print('category v ' + v)
                                category.category_description = v
                                category.save()
                                game.categories.add(category)

                        game.save()

    # Generate all genres realted to the app
    def processGenres(self, req, game, api):
        genres = req['apps'][0]['appinfo']['common'].get(
            'genres', None)
        if genres is not None:
            genreList = []
            for tag in genres.items():
                genreList.append(tag[1])
            genreRes = api.tag_request(str(game.appid), 'genres', genreList)

            if genreRes is not None:
                # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
                for item in genreRes:
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

    # Genrate primary genre
    def processPrimaryGenre(self, req, game, api):
        pg = req['apps'][0]['appinfo']['common'].get(
            'primary_genre', None)
        if pg is not None:
            tagList = []
            tagList.append(pg)
            # Send the list of tag ids we need to our function that fetches the tag description via steamAPI
            tagRes = api.tag_request(str(game.appid), 'genres', tagList)

            if tagRes is not None:
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

    # Adds languages to new game object
    def processLanguages(self, req, game):
        languagesRes = req['apps'][0]['appinfo']['common'].get(
            'supported_languages', None)
        if languagesRes is not None:
            for lang in languagesRes.keys():
                print(str(lang))
                langGet = Languages.objects.get_or_create(
                    language=str(lang))[0]
                game.supported_languages.add(langGet)
            game.save()

    # Adds app type to new game object
    def processAppType(self, req, game):
        appType = req['apps'][0]['appinfo']['common'].get(
            'type', None)
        if appType is not None:
            typeGetOrCreate = AppType.objects.get_or_create(app_type=appType)[
                0]
            game.app_type = typeGetOrCreate
            game.save()

    # Adds os options to new game object
    def processOsOptions(self, req, game):
        oslist = req['apps'][0]['appinfo']['common'].get(
            'oslist', None)
        if oslist is not None:
            # If there is an OSList, split the list by ',' delimiter
            oslist = oslist.split(',')
            # For each of those OS', check for their type and add them to the model
            for os in oslist:
                print(os)
                if (os == 'windows'):
                    game.os.add(
                        OSOptions.objects.get_or_create(os=OSOptions.WIN)[0])
                elif (os == 'macos'):
                    game.os.add(
                        OSOptions.objects.get_or_create(os=OSOptions.MAC)[0])
                elif (os == 'linux'):
                    game.os.add(
                        OSOptions.objects.get_or_create(os=OSOptions.LIN)[0])
            game.save()

    # Adds associations (developer, publisher) to new game object
    def processAssociations(self, req, game):
        assoc = req['apps'][0]['appinfo']['common'].get(
            'associations', None)
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

    #####################################################
    # Update an app that already exists in our database #
    #####################################################
    def processExistingGame(self, appid, changenum, worker, api):
        # Grab the game info from the steamkit worker
        gameInfo = worker.get_product_info(appids=[appid])
        gameInfo = gameInfo['apps'][0]['appinfo']['common']

        # Set changenumber
        self.changenum = changenum

        # Grab the game object we are checking for changes on
        game = Game.objects.get(appid=appid)

        # Checks to make
        self.easyCheckFields(game, gameInfo)
        self.intCheckFields(game, gameInfo)
        self.boolFieldChecks(game, gameInfo)
        self.priceChangeCheck(game, api.priceRequest(game.appid))
        self.categoryUpdate(game, gameInfo, api)
        self.genreUpdate(game, gameInfo, api)
        self.primaryGenreUpdate(game, gameInfo, api)
        self.associationsUpdate(game, gameInfo)
        self.appTypeUpdate(game, gameInfo)
        self.osListUpdate(game, gameInfo)
        self.languageUpdate(game, gameInfo)

    # Checks all non relational string represented fields (ex. name, release_state, icon, etc.)
    def easyCheckFields(self, game, gameInfo):
        easyFieldChecks = [
            'name', 'release_state', 'icon', 'logo', 'logo_small', 'clienticon', 'controller_support',
            'metacritic_score', 'metacritic_fullurl'
        ]

        # For each easily checkable field, run compareCharField()
        for field in easyFieldChecks:
            # if the field exists in the response
            if gameInfo.get(field):
                # If the chars are equal, no change has happened
                if str(getattr(game, field)) == str(gameInfo[field]):
                    pass
                # Else, a change did occur for a field so return the new val so we can set it in our DB
                else:
                    # Get old value before we update it so we can show it in the changelog
                    outdatedVal = getattr(game, field)
                    # Set the new updated value
                    setattr(game, field, gameInfo[field])
                    # If the name field changed, we also need to reslug our object to reflect the new name
                    if field == 'name':
                        game.slug = slugify(
                            gameInfo[field], allow_unicode=True)
                    game.save()

                    # Build out log for the change that happened and register it
                    payload = str(field) + ' updated: ' + \
                        str(outdatedVal) + \
                        ' => ' + str(gameInfo[field])
                    gameChange = GameChange(
                        change_number=self.changenum,
                        game=game,
                        changelog=GameChange.changelog_builder(
                            GameChange.UPDATE,
                            game.appid,
                            payload=payload
                        ),
                        action=GameChange.UPDATE
                    )
                    gameChange.save()
            else:
                pass

    def intCheckFields(self, game, gameInfo):
        intFieldChecks = ['review_score', 'review_percentage']

        for field in intFieldChecks:
            if gameInfo.get(field):
                # If the chars are equal, no change has happened
                if int(getattr(game, field)) == int(gameInfo[field]):
                    pass
                # Else, a change did occur for a field so return the new val so we can set it in our DB
                else:
                    outdatedVal = getattr(game, field)
                    if gameInfo[field] is not None:
                        setattr(game, field, int(gameInfo[field]))
                    else:
                        setattr(game, field, None)
                    game.save()

                    payload = str(field) + ' updated: ' + \
                        str(int(outdatedVal)) + ' => ' + \
                        str(int(gameInfo[field]))
                    gameChange = GameChange(
                        change_number=self.changenum,
                        game=game,
                        changelog=GameChange.changelog_builder(
                            GameChange.UPDATE,
                            game.appid,
                            payload=payload
                        ),
                        action=GameChange.UPDATE
                    )
                    gameChange.save()
            else:
                pass

    def boolFieldChecks(self, game, gameInfo):
        boolFieldChecks = ['community_visible_stats',
                           'workshop_visible', 'community_hub_visible']

        for field in boolFieldChecks:
            if gameInfo.get(field):
                # If the chars are equal, no change has happened
                if bool(getattr(game, field)) == bool(gameInfo[field]):
                    pass
                # Else, a change did occur for a field so return the new val so we can set it in our DB
                else:
                    outdatedVal = getattr(game, field)
                    print('bool field changed...')
                    if gameInfo[field] is not None:
                        setattr(game, field, self.boolify(gameInfo[field]))
                    else:
                        setattr(game, field, None)
                    game.save()

                    payload = str(field) + ' updated: ' + \
                        str(bool(outdatedVal)) + ' => ' + \
                        str(bool(gameInfo[field]))
                    gameChange = GameChange(
                        change_number=self.changenum,
                        game=game,
                        changelog=GameChange.changelog_builder(
                            GameChange.UPDATE,
                            game.appid,
                            payload=payload
                        ),
                        action=GameChange.UPDATE
                    )
                    gameChange.save()
            else:
                pass

    def priceChangeCheck(self, game, apiPrice):
        # Check if current price matches the current price in the DB
        if game.current_price.price != apiPrice:
            print('price mismatch')
            # Create a new price object
            price = Price(
                price=apiPrice
            )
            price.save()
            # Add that price to the game we got the price for
            game.prices.add(price)
            # Set the current price of that app to the new price we just created
            game.current_price = price
            game.save()

            payload = 'Updated app price to: ' + str(game.current_price.price)
            gameChange = GameChange(
                change_number=self.changenum,
                game=game,
                changelog=GameChange.changelog_builder(
                    GameChange.UPDATE,
                    game.appid,
                    payload=payload
                ),
                action=GameChange.UPDATE
            )
            gameChange.save()

    def categoryUpdate(self, game, gameInfo, api):
        categories = gameInfo.get('category', None)

        if categories is not None:
            catList = []
            for cat in categories:
                catList.append(cat.split('_')[1])
            catRes = api.tag_request(str(game.appid), 'categories', catList)
            catList = []

            if catRes is not None:
                # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
                for item in catRes:
                    for k, v in item.items():
                        # When the key is ID, check if that genre exists in our genre model
                        if (k == 'id'):
                            if Category.objects.filter(category_id=v).exists():
                                category = Category.objects.get(category_id=v)
                                # Check if category is associated with the game
                                if game.categories.filter(category_id=v).exists():
                                    print(
                                        'Category is already assocated with the game')
                                else:
                                    game.categories.add(category)

                                    payload = 'Added ' + category.category_description + \
                                        ' to ' + game.name + '\'s categories'
                                    gameChange = GameChange(
                                        change_number=self.changenum,
                                        game=game,
                                        changelog=GameChange.changelog_builder(
                                            GameChange.UPDATE,
                                            game.appid,
                                            payload=payload
                                        ),
                                        action=GameChange.UPDATE
                                    )
                                    gameChange.save()
                            else:
                                # If the genre doesn't exist in our genre model, create it
                                category = Category.objects.create(
                                    category_id=v)

                        elif (k == 'description'):
                            # If the desciption for the genre is not yet set, set it and associate game with the genre
                            if not category.category_description:
                                print('category v ' + v)
                                category.category_description = v
                                category.save()

                                payload = 'Added ' + category.category_description + ' category to the database'
                                gameChange = GameChange(
                                    change_number=self.changenum,
                                    game=game,
                                    changelog=GameChange.changelog_builder(
                                        GameChange.UPDATE,
                                        game.appid,
                                        payload=payload
                                    ),
                                    action=GameChange.UPDATE
                                )
                                gameChange.save()

                                game.categories.add(category)

                                payload = 'Added ' + category.category_description + \
                                    ' to ' + game.name + '\'s categories'
                                gameChange = GameChange(
                                    change_number=self.changenum,
                                    game=game,
                                    changelog=GameChange.changelog_builder(
                                        GameChange.UPDATE,
                                        game.appid,
                                        payload=payload
                                    ),
                                    action=GameChange.UPDATE
                                )
                                gameChange.save()

                        catList.append(category.category_description)

                        game.save()

                # Remove categories not in the list anymore (got removed)
                for category in game.categories.all():
                    if category.category_description not in catList:
                        game.categories.remove(category)
                        game.save()

                        payload = 'Removed ' + category.category_description + \
                            ' from ' + game.name + '\'s categories'
                        gameChange = GameChange(
                            change_number=self.changenum,
                            game=game,
                            changelog=GameChange.changelog_builder(
                                GameChange.UPDATE,
                                game.appid,
                                payload=payload
                            ),
                            action=GameChange.UPDATE
                        )
                        gameChange.save()

    def genreUpdate(self, game, gameInfo, api):
        tags = gameInfo.get('genres', None)

        if tags is not None:
            tagList = []
            for tag in tags.items():
                tagList.append(tag[1])
            tagRes = api.tag_request(str(game.appid), 'genres', tagList)
            genreList = []

            if tagRes is not None:
                # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
                for item in tagRes:
                    for k, v in item.items():
                        # When the key is ID, check if that genre exists in our genre model
                        if (k == 'id'):
                            if Genre.objects.filter(genre_id=v).exists():
                                genre = Genre.objects.get(genre_id=v)
                                # Check if genre is associated with the game
                                if game.genres.filter(genre_id=v).exists():
                                    print(
                                        'Genre is already associated with the game')
                                else:
                                    game.genres.add(genre)

                                    payload = 'Added ' + genre.genre_description + \
                                        ' to ' + game.name + '\'s genres'
                                    gameChange = GameChange(
                                        change_number=self.changenum,
                                        game=game,
                                        changelog=GameChange.changelog_builder(
                                            GameChange.UPDATE,
                                            game.appid,
                                            payload=payload
                                        ),
                                        action=GameChange.UPDATE
                                    )
                                    gameChange.save()
                            else:
                                # If the genre doesn't exist in our genre model, create it
                                genre = Genre.objects.create(genre_id=v)
                        elif (k == 'description'):
                            # If the desciption for the genre is not yet set, set it and associate game with the genre
                            if not genre.genre_description:
                                print('genre v ' + v)
                                genre.genre_description = v
                                genre.save()

                                payload = 'Added ' + genre.genre_description + ' genre to the database'
                                gameChange = GameChange(
                                    change_number=self.changenum,
                                    game=game,
                                    changelog=GameChange.changelog_builder(
                                        GameChange.UPDATE,
                                        game.appid,
                                        payload=payload
                                    ),
                                    action=GameChange.UPDATE
                                )
                                gameChange.save()

                                game.genres.add(genre)

                                payload = 'Added ' + genre.genre_description + \
                                    ' to ' + game.name + '\'s genres'
                                gameChange = GameChange(
                                    change_number=self.changenum,
                                    game=game,
                                    changelog=GameChange.changelog_builder(
                                        GameChange.UPDATE,
                                        game.appid,
                                        payload=payload
                                    ),
                                    action=GameChange.UPDATE
                                )
                                gameChange.save()

                        genreList.append(genre.genre_description)

                        game.save()

                for genre in game.genres.all():
                    if genre.genre_description not in genreList:
                        game.genres.remove(genre)

                        payload = 'Removed ' + genre.genre_description + \
                            ' from ' + game.name + '\'s genres'
                        gameChange = GameChange(
                            change_number=self.changenum,
                            game=game,
                            changelog=GameChange.changelog_builder(
                                GameChange.UPDATE,
                                game.appid,
                                payload=payload
                            ),
                            action=GameChange.UPDATE
                        )
                        gameChange.save()

    def primaryGenreUpdate(self, game, gameInfo, api):
        pg = gameInfo.get('primary_genre', None)
        if pg is not None:
            tagList = []
            tagList.append(pg)
            # Send the list of tag ids we need to our function that fetches the tag description via steamAPI
            tagRes = api.tag_request(str(game.appid), 'genres', tagList)

            if tagRes is not None:
                # For each item in the response, get the k, v of each item (k= 'id', 'descriptions' | v= 'idOfTag', 'textDesciptionOfTag')
                for item in tagRes:
                    for k, v in item.items():
                        # When the key is ID, check if that genre exists in our genre model
                        if (k == 'id'):
                            if Genre.objects.filter(genre_id=v).exists():
                                genre = Genre.objects.get(genre_id=v)
                                # Check if game primary genre is up to date with the res primary genre
                                if game.primary_genre == genre:
                                    print('primary genre up to date')
                                else:
                                    game.primary_genre = genre

                                    payload = 'Updated ' + game.name + \
                                        '\'s primary genre to ' + genre.genre_description
                                    gameChange = GameChange(
                                        change_number=self.changenum,
                                        game=game,
                                        changelog=GameChange.changelog_builder(
                                            GameChange.UPDATE,
                                            game.appid,
                                            payload=payload
                                        ),
                                        action=GameChange.UPDATE
                                    )
                                    gameChange.save()

                            else:
                                # If the genre doesn't exist in our genre model, create it
                                genre = Genre.objects.create(genre_id=v)

                        elif (k == 'description'):
                            # If the desciption for the genre is not yet set, set it and associate game with the primary genre
                            if not genre.genre_description:
                                genre.genre_description = v
                                genre.save()
                                game.primary_genre = genre

                                payload = 'Updated ' + game.name + \
                                    '\'s primary genre to ' + genre.genre_description
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

                        game.save()

    # Assocations (publishers and developers for a given app)
    def associationsUpdate(self, game, gameInfo):
        assoc = gameInfo.get('associations', None)
        # Lists we will use to see if anything has been removed from the game we stored in our DB
        devList = []
        pubList = []
        if assoc is not None:
            # Loop through each association  through .values()
            for a in assoc.values():
                # If type is developer, either get the existing developer from our model or create one and associate it with our game
                if a['type'] == 'developer':
                    devList.append(a['name'])
                    if game.developer.filter(developer=a['name']).exists():
                        print(a['name'] + ' is already in the db')
                    else:
                        print(a['name'] + ' is not in the DB. Adding to the DB...')
                        devGet = Developer.objects.get_or_create(
                            developer=str(a['name']))[0]
                        game.developer.add(devGet)
                        game.save()

                        payload = 'Added ' + devGet.developer + ' to ' + game.name + ' developers.'
                        gameChange = GameChange(
                            change_number=self.changenum,
                            game=game,
                            changelog=GameChange.changelog_builder(
                                GameChange.UPDATE,
                                game.appid,
                                payload=payload
                            ),
                            action=GameChange.UPDATE
                        )
                        gameChange.save()

                    devList.append(a['name'])

                # If type is publisher, either get the existing publisher from our model or create one and associate it with our game
                else:
                    pubList.append(a['name'])
                    if game.publisher.filter(publisher=a['name']).exists():
                        print(a['name'] + ' is already in the db')
                    else:
                        print(a['name'] + ' is not in the DB. Adding to the DB...')
                        pubGet = Publisher.objects.get_or_create(
                            publisher=str(a['name']))[0]
                        game.publisher.add(pubGet)
                        game.save()

                        payload = 'Added ' + pubGet.publisher + ' to ' + game.name + ' publishers.'
                        gameChange = GameChange(
                            change_number=self.changenum,
                            game=game,
                            changelog=GameChange.changelog_builder(
                                GameChange.UPDATE,
                                game.appid,
                                payload=payload
                            ),
                            action=GameChange.UPDATE
                        )
                        gameChange.save()

                    pubList.append(a['name'])
            game.save()

        # Check if developer was removed
        for dev in game.developer.all():
            if dev.developer not in devList:
                game.developer.remove(dev)

                payload = 'Removed ' + dev.developer + ' from ' + game.name + '\'s developers.'
                gameChange = GameChange(
                    change_number=self.changenum,
                    game=game,
                    changelog=GameChange.changelog_builder(
                        GameChange.UPDATE,
                        game.appid,
                        payload=payload
                    ),
                    action=GameChange.UPDATE
                )
                gameChange.save()

        # Check if publisher was removed
        for pub in game.publisher.all():
            if pub.publisher not in pubList:
                game.publisher.remove(pub)

                payload = 'Removed ' + pub.publisher + ' from ' + game.name + '\'s publishers.'
                gameChange = GameChange(
                    change_number=self.changenum,
                    game=game,
                    changelog=GameChange.changelog_builder(
                        GameChange.UPDATE,
                        game.appid,
                        payload=payload
                    ),
                    action=GameChange.UPDATE
                )
                gameChange.save()

    def appTypeUpdate(self, game, gameInfo):
        appType = gameInfo.get('type')
        if appType is not None:
            typeGetOrCreate = AppType.objects.get_or_create(app_type=appType)[
                0]
            if game.app_type.app_type != appType:
                print('app type has changed')
                game.app_type = typeGetOrCreate
                game.save()

                payload = 'Updated app type to: ' + str(game.app_type.app_type)
                gameChange = GameChange(
                    change_number=self.changenum,
                    game=game,
                    changelog=GameChange.changelog_builder(
                        GameChange.UPDATE,
                        game.appid,
                        payload=payload
                    ),
                    action=GameChange.UPDATE
                )
                gameChange.save()

    def osListUpdate(self, game, gameInfo):
        oslist = gameInfo.get('oslist', None)

        if oslist is not None:
            osUpdated = False
            # If there is an OSList, split the list by ',' delimiter
            oslist = oslist.split(',')
            # For each of those OS', check for their type and add them to the model
            for os in oslist:
                if (os == 'windows'):
                    if game.os.filter(os=OSOptions.WIN).exists():
                        pass
                    else:
                        os = OSOptions.objects.get_or_create(
                            os=OSOptions.WIN)[0]
                        game.os.add(os)
                        osUpdated = True
                elif (os == 'macos'):
                    if game.os.filter(os=OSOptions.MAC).exists():
                        pass
                    else:
                        os = OSOptions.objects.get_or_create(
                            os=OSOptions.MAC)[0]
                        game.os.add(os)
                        osUpdated = True
                elif (os == 'linux'):
                    if game.os.filter(os=OSOptions.LIN).exists():
                        pass
                    else:
                        os = OSOptions.objects.get_or_create(
                            os=OSOptions.LIN)[0]
                        game.os.add(os)
                        osUpdated = True
            game.save()

            if 'windows' not in oslist and game.os.filter(os=OSOptions.WIN).exists():
                print('windows no longer supported')
                os = OSOptions.objects.get_or_create(os=OSOptions.WIN)[0]
                game.os.remove(os)
                game.save()
                osUpdated = True

            if 'macos' not in oslist and game.os.filter(os=OSOptions.MAC).exists():
                print('macos no longer supported')
                os = OSOptions.objects.get_or_create(os=OSOptions.MAC)[0]
                game.os.remove(os)
                game.save()
                osUpdated = True

            if 'linux' not in oslist and game.os.filter(os=OSOptions.LIN).exists():
                print('linux no longer supported')
                os = OSOptions.objects.get_or_create(os=OSOptions.LIN)[0]
                game.os.remove(os)
                game.save()
                osUpdated = True

            if osUpdated:
                gameChange = GameChange(
                    change_number=self.changenum,
                    game=game,
                    changelog=GameChange.changelog_builder(
                        GameChange.UPDATE,
                        game.appid,
                        payload='OS options updated'
                    ),
                    action=GameChange.UPDATE
                )
                gameChange.save()

    def languageUpdate(self, game, gameInfo):
        languagesRes = gameInfo.get('languages', None)
        langResCompare = []
        # Check that all languages from steamkit res are saved to our db / associated to our game
        if languagesRes is not None:
            for lang in languagesRes.keys():
                langResCompare.append(lang)
                if game.supported_languages.filter(language=lang).exists():
                    print(lang + ' is already in the db')
                else:
                    print(lang + ' is not in the DB. Adding to the DB...')
                    langGet = Languages.objects.get_or_create(
                        language=str(lang))[0]
                    game.supported_languages.add(langGet)
                    game.save()

                    payload = 'Added ' + lang + ' to ' + game.name + ' supported languages.'
                    gameChange = GameChange(
                        change_number=self.changenum,
                        game=game,
                        changelog=GameChange.changelog_builder(
                            GameChange.UPDATE,
                            game.appid,
                            payload=payload
                        ),
                        action=GameChange.UPDATE
                    )
                    gameChange.save()

            # Remove any languages that are no longer supported
            for lang in game.supported_languages.all():
                if lang.language in langResCompare:
                    print(lang.language + ' is in the response')
                else:
                    print(lang.language + ' is not in response. Removing from DB')
                    game.supported_languages.remove(lang)

                    payload = 'Deleted ' + lang.language + \
                        ' from ' + game.name + ' supported languages.'
                    gameChange = GameChange(
                        change_number=self.changenum,
                        game=game,
                        changelog=GameChange.changelog_builder(
                            GameChange.UPDATE,
                            game.appid,
                            payload=payload
                        ),
                        action=GameChange.UPDATE
                    )
                    gameChange.save()

    ##############################################
    # Utility Functions for the Model Processing #
    ##############################################

    # Checks to see if the app exists in our database, then call function accordingly
    def checkForExistance(self, appid):
        if Game.objects.filter(appid=appid).exists():
            print('Game Exists')
            self.exists = True
        else:
            print('game does not exist')
            self.exists = False
        return None

    # boolifies a steam boolean field response from 0/1 to a True,False
    def boolify(self, num):
        if num == '1':
            return True
        else:
            return False

    # Converts the returned epoch time to DateTime format to store in the database
    def epochToDateTime(self, timestamp):
        if timestamp is not None:
            return make_aware(datetime.fromtimestamp(int(timestamp)))
        else:
            return None
