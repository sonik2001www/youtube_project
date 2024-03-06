from django.contrib import admin
from parser_app import models


@admin.register(models.Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'status')


@admin.register(models.Remove)
class RemoveAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('channel_id', 'title', 'description',
                    'websites_list', 'published', 'url', 'subscribers_count',
                    'country', 'thumbnail_medium_url')


@admin.register(models.Video)
class VideolAdmin(admin.ModelAdmin):
    list_display = ('name', 'video_id', 'channel_id', 'websites_list',
                    'published', 'url', 'views_count', 'tags',
                    'thumbnail_medium_url', 'status')


@admin.register(models.Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


@admin.register(models.Quota)
class QuotaAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'requests')


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo', 'domain', 'industries', 'key_people',
                    'country')


@admin.register(models.DealInfo)
class DealInfoAdmin(admin.ModelAdmin):
    list_display = ('brand', 'date', 'name', 'email', 'phone_number', 'archive')


@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_requests')


###########################################################################
# SALES #


@admin.register(models.DrugAndDoorField)
class DrugAndDoorFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'drug_and_door_col', 'position', 'stars')


@admin.register(models.DrugAndDoorCol)
class DrugAndDoorFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'position')

