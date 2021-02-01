# Generated by Django 3.1.5 on 2021-01-29 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_auto_20210129_2112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='listing',
            options={'ordering': ['-last_modified']},
        ),
        migrations.RemoveField(
            model_name='listing',
            name='bidders',
        ),
        migrations.AddField(
            model_name='comment',
            name='comment_text',
            field=models.TextField(max_length=350, null=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='comment_timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(max_length=250),
        ),
    ]
