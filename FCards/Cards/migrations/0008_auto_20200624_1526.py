# Generated by Django 3.0.7 on 2020-06-24 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0007_auto_20200624_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='pronunciation',
            field=models.CharField(blank=True, default=False, max_length=200, null=True),
        ),
    ]