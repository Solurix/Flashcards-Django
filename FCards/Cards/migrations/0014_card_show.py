# Generated by Django 3.0.7 on 2020-07-04 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0013_auto_20200630_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='show',
            field=models.BooleanField(default=False),
        ),
    ]
