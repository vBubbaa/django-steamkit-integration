# Generated by Django 2.2.7 on 2020-07-02 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0023_auto_20200411_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='genres',
            field=models.ManyToManyField(related_name='genres', to='game.Genre'),
        ),
    ]
