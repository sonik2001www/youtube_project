# Generated by Django 4.2.3 on 2023-09-08 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0014_alter_channel_channel_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='next_page_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
