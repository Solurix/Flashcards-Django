# Generated by Django 3.0.7 on 2020-06-26 07:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Cards', '0008_auto_20200624_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='cards_folder',
            field=models.ForeignKey(default=False, on_delete=django.db.models.deletion.CASCADE, to='Cards.CardFolder'),
            preserve_default=False,
        ),
    ]