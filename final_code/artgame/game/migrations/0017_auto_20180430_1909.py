# Generated by Django 2.0.2 on 2018-04-30 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='category',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Category'),
        ),
    ]
