# Generated by Django 2.2.7 on 2020-03-08 23:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0019_auto_20200307_1547'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='app_type',
        ),
        migrations.AddField(
            model_name='game',
            name='app_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='type', to='game.AppType'),
        ),
    ]