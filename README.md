# django-steamkit-integration
An integration of the python ported steamkit library to monitor steamapps (create new apps | edit existing apps).

## Table of Contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Usage](#usage)
4. [How does this work?](#how)
5. [What does this script NOT do](#notdo)
6. [Why was this made?](#why)

## Requirements <a name="requirements"></a>
- Python 3+
- Django 2+
- [Steamkit python port 'Steam'](https://github.com/ValvePython/steam)
- djangorestframework
- django-cors-headers
- django-allauth
- virtualenv _optional for production_

## Installation <a name="installation"></a>
- Clone the [repo](https://github.com/vBubbaa/django-steamkit-integration)
- Install all pipfile dependecies

## Usage <a name="usage"></a>
> Note that this code is highly customized to fit SteamComparer's needs
- To run an app test (see if steam if working), open `$rootdir>game>management>commands>AppTest.py` and change the `appid` value to whichever appid you wish to get information for, and change the `processor` method to either: `processNewGame` or `processExistingGame` (depending on if you already have the app in the database)
- *LINUX*: Configure the scripts.sh file to activate your own virtualenv, cd into the projects $rootdir, and run this script as a crontab, or manually run scout.py (located in `$rootdir>game>management>commands>`).
- *Windows*: Support is limited and untested currently. You will need to manually run scout.py.
`Scout.py` handles scanning steam consistently, and creating tasks when given new appchanges provided by steam. It also handles dispatching app creation and app updating given the steam changenumber and appid provided.

## How does this work? <a name="how"></a>
This uses the Django web framework along with management commands to create a management command `scout.py`, which dispatches either `processNewGame` or `processExistingGame` depending on if the app exists in the database. This script is meant to run long term and consistently monitor steam and track all changes.

When a user logs in and accesses their game library or compares with friends, if any games in the libraries do not exist in our database, we create a task to process that app.

To monitor Steam, we use the awesome [Steam](https://github.com/ValvePython/steam) (python steamkit port)

Steam allows us to monitor the steamclient itself and get changenumbers along with appids to tell us when a steam app has been added or updated. From there we take that appid and either create a new app in our database or we edit the app if it already exists in our database.

We use the basic [SteamAPI](https://developer.valvesoftware.com/wiki/Steam_Web_API) to get information for game prices, user information/game libraries, as well as to get tags (Genres, Primary Genres, and Categories) because steamkit does not get the tags, it only returns the id of the tag and not the string representation of the tag (ex. 'Action', 'Massive Online Multiplayer')

We use [SteamSpy](https://steamspy.com/) to gather addional information on applications such as player counts, and average playtimes.

## What does this script NOT do? <a name="notdo"></a>
- We don't store EVERYTHING that steamkit shows us, such as depots and some other information.

## Why was this made? <a name="why"></a>
This was made to be a backend for [SteamComparer](https://steamcomparer.com/) which consistently keeps our application up to date and lets us track application changes. The original idea for the site, was to allow users to easily login and compare game libraries with x amount of friends. We always found ourselves asking "What game do you want to play? Lets play something new, what other games do we have in common?". Our website is the answer to that question with our library comparison functionality. 
