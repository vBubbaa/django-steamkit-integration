#!/bin/bash

cd /root/django-steamkit-integration

python3 ./manage.py ClientUpdater
python3 ./manage.py TaskUpdater
