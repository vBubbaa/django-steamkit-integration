#!/bin/bash

cd /root/django-steamkit-integration

/usr/lib/python3.6 ./manage.py ClientUpdater
/usr/lib/python3.6 ./manage.py TaskUpdater
