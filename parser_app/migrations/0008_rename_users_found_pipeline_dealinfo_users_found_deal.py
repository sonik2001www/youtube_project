# Generated by Django 4.2.3 on 2023-09-04 07:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0007_dealinfo_users_found_pipeline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dealinfo',
            old_name='users_found_pipeline',
            new_name='users_found_deal',
        ),
    ]
