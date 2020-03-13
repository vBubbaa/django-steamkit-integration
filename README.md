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

## Installation <a name="installation"></a>
- Clone the [repo](https://github.com/vBubbaa/django-steamkit-integration)
- Install all pipfile dependecies

## Usage <a name="usage"></a>
- To test adding a new app to the database run `python manage.py newGameTest` 
- To test editing a preexisting app in the database rune `python manage.py editGameTest`
- To run the monitoring script that adds apps and edits preexisting games run `python manage.py ClientUpdater`

## How does this work? <a name="how"></a>
This uses the Django web framework along with management commands to create a management command that constantly checks for updated applications and either adds the app to the database, or if it already exists it checks all fields in the database and edits anything that changed.

To monitor Steam, we use the awesome [Steam](https://github.com/ValvePython/steam) (python steamkit port)

Steam allows us to monitor the steamclient itself and get changenumbers along with appids to tell us when a steam app has been added or updated. From there we take that appid and either create a new app in our database or we edit the app if it already exists in our database.

We use the basic [SteamAPI](https://developer.valvesoftware.com/wiki/Steam_Web_API) to get information for game prices as well as to get tags (Genres, Primary Genres, and Categories) because steamkit does not get the app prices and the tags only return the id of the tag and not the string representation of the tag (ex. 'Action', 'Massive Online Multiplayer')

## What does this script NOT do? <a name="notdo"></a>
- We don't store EVERYTHING that steamkit shows us, such as depots and some other information that I am not interested in.

## Why was this made? <a name="why"></a>
This was made to support my personal project [SteamComparer](https://steamcomparer.com/). That project was getting all information from the WebAPI as well as WebScraping. The problem with that is I didn't know when anything for an application was updated it simply uses cron jobs to scrape steam and get information. With SteamKit we can get changes and updates when they happen plug get a ton of useful information.
