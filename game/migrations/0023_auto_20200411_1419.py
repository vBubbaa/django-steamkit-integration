# Generated by Django 2.2.7 on 2020-04-11 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0022_auto_20200411_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='community_hub_visible',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='community_visible_stats',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='workshop_visible',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
