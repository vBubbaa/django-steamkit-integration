# Generated by Django 2.2.7 on 2020-02-28 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_auto_20200128_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='clienttga',
        ),
    ]
