#!/bin/bash

cd /root/django-steamkit-integration

/usr/lib/python3.6 ./manage.py ClientUpdater >> /root/clientlogs.log 2>&1
/usr/lib/python3.6 ./manage.py TaskUpdater >> /root/tasklogs.log 2>&1
