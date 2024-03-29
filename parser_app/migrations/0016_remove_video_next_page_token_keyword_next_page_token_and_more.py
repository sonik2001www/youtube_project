# Generated by Django 4.2.3 on 2023-09-08 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0015_video_next_page_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='next_page_token',
        ),
        migrations.AddField(
            model_name='keyword',
            name='next_page_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='keyword',
            name='users_found_keyword',
            field=models.ManyToManyField(to='parser_app.profile'),
        ),
    ]
