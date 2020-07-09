# Generated by Django 2.2.7 on 2020-01-18 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appid', models.IntegerField()),
                ('name', models.CharField(max_length=264)),
                ('slug', models.SlugField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
            ],
        ),
    ]