#!/usr/bin/env python3
import re
import requests
from . import load_django
from pprint import pprint
from itertools import cycle
from typing import Optional
from datetime import datetime
from parser_app import models
from .utils import tokens, topic_ids, chain
from django.db.utils import DataError
import concurrent.futures


def get_channel(user_id: int, channel_id: str) -> Optional[dict]:
    user = models.Profile.objects.get(user__id=user_id)
    if user.plan_availiable_requests <= 0:
        return 'limit'

    response = requests.get(
        f'https://www.googleapis.com/youtube/v3/channels?'
        f'part=snippet,brandingSettings,contentDetails,'
        f'contentOwnerDetails,localizations,statistics,status,'
        f'topicDetails&key={next(tokens)}&id={channel_id}'
    )

    user.channel_requests += 1
    user.total_requests += 1
    user.plan_availiable_requests -= 1
    user.save()

    payload = response.json()

    if payload.get('error'):
        return

    channel = None

    try:
        channel = payload['items'][0]
    except:
        return
    description = channel['snippet']['description']
    email_match = re.search(r'[a-z0-9+-_.]+@[a-z0-9+-_.]+\.[a-z]+', description)
    email = email_match.group() if email_match else None
    url = (
        chain(channel, 'snippet', 'customUrl') and
        'https://www.youtube.com/' + channel['snippet']['customUrl']
    )

    published_at = channel['snippet']['publishedAt']
    if len(published_at) == 20:
        published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
    else:
        published = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S.%fZ')

    youtube_categories = []
    for id in chain(channel, 'topicDetails', 'topicIds', default=[]):
        try:
            youtube_categories.append(topic_ids[id])
        except KeyError:
            continue
    return {
        'url': url,
        'email': email,
        'published': published,
        'description': description,
        'youtube_categories': youtube_categories,
        'title': channel['brandingSettings']['channel']['title'],
        'video_count': chain(channel, 'statistics', 'videoCount'),
        'websites_list': re.findall(r'(https?://\S+)', description),
        'subscribers_count': channel['statistics']['subscriberCount'],
        'country_code': chain(channel, 'brandingSettings', 'channel', 'country'),
        'thumbnail_medium_url': channel['snippet']['thumbnails']['medium']['url'],
    }


def search_channels(user_id: int, query: str, count: int = 4, more_than: int = None,
                    less_than: int = None, country_code: str = None):

    user = models.Profile.objects.get(user__id=user_id)
    if user.plan_availiable_requests <= 0:
        return 'limit'

    page_token = ''
    print(count, '---========')
    for i in range(count // 4):
        print('start--', i)

        response = requests.get(
            f'https://www.googleapis.com/youtube/v3/search?'
            f'part=snippet&maxResults={count}&q={query}&type=channel&'
            f'key={next(tokens)}&pageToken={page_token}'
        )

        user.search_requests += 1
        user.total_requests += 1
        user.plan_availiable_requests -= 1
        user.save()

        payload = response.json()
        page_token = payload.get('nextPageToken', '')

        channels_to_delete = models.Channel.objects.filter(users_found_channel=user)
        if channels_to_delete:
            channels_to_delete.delete()

        if not payload.get('error'):
            for item in payload['items']:
                channel_id = item['snippet']['channelId']
                channel = get_channel(user_id=user_id, channel_id=channel_id)
                if not channel or channel == 'limit':
                    continue

                country = channel.pop('country_code')
                is_country_code_matching = (
                    country_code == '' or country_code is None or (
                        country is not None and
                        country_code.upper() == country.upper()
                    )
                )
                if not is_country_code_matching:
                    continue

                is_more_than_matching = more_than is None or (
                    channel['subscribers_count'] is not None and
                    more_than <= int(channel['subscribers_count'])
                )
                if not is_more_than_matching:
                    continue

                is_less_than_matching = less_than is None or (
                    channel['subscribers_count'] is not None and
                    less_than >= int(channel['subscribers_count'])
                )
                if not is_less_than_matching:
                    continue

                if country:
                    channel['country'] = models.Country.objects.get(
                        code=country
                    )
                else:
                    channel['country'] = None

                print('\n---\n')
                obj = models.Channel.objects.create(
                    channel_id=channel_id,
                    url=channel['url'],
                    email=channel['email'],
                    published=channel['published'],
                    description=channel['description'],
                    youtube_categories=channel['youtube_categories'],
                    title=channel['title'],
                    video_count=channel['video_count'],
                    websites_list=channel['websites_list'],
                    subscribers_count=channel['subscribers_count'],
                    thumbnail_medium_url=channel['thumbnail_medium_url'],
                    country=channel['country'],
                )
                obj.users_found_channel.add(user)


def search_videos(user_id: models.User, count: int = 50, page_token: str = ''):
    user = models.Profile.objects.get(user__id=user_id)
    if user.plan_availiable_requests <= 0:
        return 'limit'

    channel_name = models.Settings.objects.get(name='Channel Name').value
    date_before, date_after, country_code, shorts = (
        f'{models.Settings.objects.get(name="Date Before").value}T00:00:00Z',
        f'{models.Settings.objects.get(name="Date After").value}T00:00:00Z',
        f'{models.Settings.objects.get(name="Country").value}',
        models.Settings.objects.get(name="Shorts").value
    )

    country_code = '' if country_code == 'All' else f'&regionCode={country_code}'
    shorts = '' if shorts == 'True' else '&videoDuration=medium'

    print('\n------------------\n\n\n')
    print(country_code)
    print(f'&publishedAfter={date_after} publishedBefore={date_before}')
    print('\n------------------\n\n\n')

    user.search_requests += 1
    user.total_requests += 1
    user.plan_availiable_requests -= 1
    user.save()

    keyword = models.Keyword.objects.filter(users_found_keyword=user).latest('id')
    print(keyword.name)
    print(page_token)

    if page_token == '' and page_token != 'page_token_last':
        videos_to_delete = models.Video.objects.filter(users_found_video=user)
        if videos_to_delete:
            videos_to_delete.delete()

    if keyword.status == 'New' or (page_token != '' and page_token != 'page_token_last'):
        for i in range(count // 50):

            response = requests.get(
                f'https://www.googleapis.com/youtube/v3/search?'
                f'part=snippet&maxResults=50&q={keyword}{country_code}&type=video&'
                f'order=viewCount&key={next(tokens)}&pageToken={page_token}&'
                f'channelId={channel_name}&publishedAfter={date_after}&'
                f'publishedBefore={date_before}{shorts}'
            )

            payload = response.json()
            page_token = payload.get('nextPageToken', '')

            if not payload.get('error'):

                for video in payload['items']:
                    url_prefix = 'https://www.youtube.com/watch?v='
                    video_id = video['id']['videoId']
                    published_at = video['snippet']['publishedAt']
                    if len(published_at) == 20:
                        published = datetime.strptime(
                            published_at,
                            "%Y-%m-%dT%H:%M:%SZ"
                        )
                    else:
                        published = datetime.strptime(
                            published_at,
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        )

                    obj = models.Video.objects.create(
                        video_id=video_id,
                        name=video['snippet']['title'],
                        channel_id=video['snippet']['channelId'],
                        published=published,
                        url=url_prefix + video_id,
                        websites_list=[],
                        tags=[],
                    )
                    created = True
                    obj.users_found_video.add(user)

        print('page_token ----------------------', page_token)

        if page_token == '':
            keyword.next_page_token = 'page_token_last'
        else:
            keyword.next_page_token = page_token
        keyword.status = 'Done'
        keyword.save()


def add_video_data_pool(ls):

    user = ls[1]
    video = ls[0]

    if True:
        response = requests.get(
            f'https://www.googleapis.com/youtube/v3/videos?'
            f'part=contentDetails,liveStreamingDetails,localizations,player,'
            f'recordingDetails,snippet,statistics,status,topicDetails&'
            f'key={next(tokens)}&id={video.video_id}'
        )

        user.video_requests += 1
        user.total_requests += 1
        user.plan_availiable_requests -= 1
        user.save()

        payload = response.json()
        if payload.get('error'):
            return 0

        # import pprint
        #
        # pprint.pprint(payload)

        try:
            description = payload['items'][0]['snippet']['description']
            websites_list = re.findall(r'(https?://[^\s]+)', description)
            try:
                video.views_count = payload['items'][0]['statistics']['viewCount']
            except:
                video.views_count = 0
            video.tags = chain(payload, 'items', 0, 'snippet', 'tags', default=[])
            video.thumbnail_medium_url = payload['items'][0]['snippet']['thumbnails']['medium']['url']

            cleaned_websites_list = []

            # 1 comment

            if True:
                response = requests.get(
                    f'https://www.googleapis.com/youtube/v3/commentThreads?'
                    f'part=snippet,id&'
                    f'key={next(tokens)}&videoId={video.video_id}'
                )

                user.video_requests += 1
                user.total_requests += 1
                user.plan_availiable_requests -= 1
                user.save()

                payload = response.json()

                try:
                    top_comment = payload['items'][0]['snippet']['topLevelComment']['snippet']['textDisplay']
                    websites_list_comment = re.findall(r'(https?://[^\s]+)', top_comment)
                    for link in websites_list_comment:
                        cleaned_link = link.split('"')[0]
                        cleaned_websites_list.append("&&" + cleaned_link)
                except:
                    cleaned_websites_list = []

            video.websites_list = cleaned_websites_list + websites_list

            channel_is = models.Channel.objects.filter(channel_id=video.channel_id, users_found_channel=None)

            if not channel_is.exists():

                channel = get_channel(user_id=user.user_id, channel_id=video.channel_id)

                if channel:
                    country = channel.pop('country_code')

                    if country:
                        channel['country'] = models.Country.objects.get(
                            code=country
                        )
                    else:
                        channel['country'] = None

                    models.Channel.objects.create(
                        channel_id=video.channel_id,
                        url=channel['url'],
                        email=channel['email'],
                        published=channel['published'],
                        description=channel['description'],
                        youtube_categories=channel['youtube_categories'],
                        title=channel['title'],
                        video_count=channel['video_count'],
                        websites_list=channel['websites_list'],
                        subscribers_count=channel['subscribers_count'],
                        thumbnail_medium_url=channel['thumbnail_medium_url'],
                        country=channel['country'],
                    )

            try:
                video.status = 'Done'
                video.save()
            except DataError:
                return 0
        except:
            print('----------------------------------------------')
            print('----------------P R O B L E M-----------------')
            print('----------------------------------------------')


def add_video_data(user_id: models.User):

    user = models.Profile.objects.get(user__id=user_id)
    if user.plan_availiable_requests <= 0:
        return 'limit'

    lst = []

    for v in models.Video.objects.filter(views_count=None):
        lst.append([v, user])

    try:
        add_video_data_pool(lst[0])
    except:
        print('no videos')

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    futures = executor.map(add_video_data_pool, lst[1:])

    # wait for all the tasks in the executor to finish
    if futures:
        executor.shutdown()

    # for i in lst:
    #     add_video_data_pool(i)

    print('---\n\nend----\n\n----')

def remove_websites():
    pass
