# Generated by Django 3.0.7 on 2020-06-29 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0009_card_cards_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='mastered',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='multicard',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]