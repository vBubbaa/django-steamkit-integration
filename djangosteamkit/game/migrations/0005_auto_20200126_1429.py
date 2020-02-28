# Generated by Django 2.2.7 on 2020-01-26 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_auto_20200126_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='os',
            field=models.ManyToManyField(null=True, to='game.OSOptions'),
        ),
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7, null=True),
        ),
    ]