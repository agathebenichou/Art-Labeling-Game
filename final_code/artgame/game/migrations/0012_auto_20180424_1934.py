# Generated by Django 2.0.2 on 2018-04-24 19:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_auto_20180424_1928'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ['-total_score']},
        ),
    ]
