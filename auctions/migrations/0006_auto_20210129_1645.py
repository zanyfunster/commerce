# Generated by Django 3.1.5 on 2021-01-29 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_listing_last_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='last_modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]