# Generated by Django 3.1.5 on 2021-01-28 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_listing_current_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='slug',
            field=models.SlugField(blank=True, max_length=20, null=True),
        ),
    ]
