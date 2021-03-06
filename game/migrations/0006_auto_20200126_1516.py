# Generated by Django 2.2.7 on 2020-01-26 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_auto_20200126_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='os',
            field=models.ManyToManyField(to='game.OSOptions'),
        ),
        migrations.AlterField(
            model_name='osoptions',
            name='os',
            field=models.CharField(choices=[('WIN', 'Windows'), ('MAC', 'MacOS'), ('LIN', 'Linux')], max_length=10),
        ),
    ]
