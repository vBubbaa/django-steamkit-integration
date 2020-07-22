#!/bin/bash

## Crontab Config: 
## @reboot . $HOME/.profile; /root/django-steamkit-integration/scripts.sh > /root/cronjob.log 2>&1

source /root/django-steamkit-integration/scenv/bin/activate

cd /root/django-steamkit-integration

/root/django-steamkit-integration/scenv/bin/python3.7 manage.py ClientUpdater >> /root/clientupdater.log 2>&1
/root/django-steamkit-integration/scenv/bin/python3.7 manage.py TaskUpdater >> /root/taskupdater.log 2>&1

