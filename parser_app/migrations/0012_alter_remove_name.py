# Generated by Django 4.2.3 on 2023-09-06 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0011_remove_users_found_remove'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remove',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
