# Generated by Django 3.0.7 on 2020-06-29 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0012_auto_20200629_2236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='multicard',
            name='score',
            field=models.SmallIntegerField(default=0),
        ),
    ]
