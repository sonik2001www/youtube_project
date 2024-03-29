# Generated by Django 4.2.3 on 2023-08-30 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0002_video_keyword'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('docfile', models.FileField(upload_to='media/documents/')),
            ],
        ),
        migrations.AddField(
            model_name='dealinfo',
            name='comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='dealinfo',
            name='document',
            field=models.ManyToManyField(blank=True, to='parser_app.document'),
        ),
    ]
