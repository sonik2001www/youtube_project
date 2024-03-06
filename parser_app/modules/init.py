#!/usr/bin/env python3
import io
import bs4
import sys
import load_django
import requests as req
from parser_app import models
from django.core.files import File


def countries():
    res = req.get('https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes')
    soup = bs4.BeautifulSoup(res.content, 'html.parser')

    for tr in soup.find('table', class_='wikitable').select('tr'):
        try:
            res = req.get('https:' + tr.select_one('td:nth-child(1) img')['src'])
            name = tr.select_one('td:nth-child(1) > a').text.replace('(the)', '').strip()
            filename = name.lower().replace(' ', '_') + '.svg.png'

            models.Country.objects.create(
                code=tr.select_one('td:nth-child(4)').get_text().strip(),
                name=name,
                flag=File(io.BytesIO(res.content), name=filename)
            )
        except:
            pass


def setup():
    models.Settings.objects.create(name='Channel Name', value='')
    models.Settings.objects.create(name='Date After', value='2000-01-01')
    models.Settings.objects.create(name='Date Before', value='2023-12-31')
    models.Quota.objects.create(name='default', price=0, requests=0)
    models.Quota.objects.create(name='Low', price=39, requests=5000)
    models.Quota.objects.create(name='Medium', price=99, requests=15000)
    models.Quota.objects.create(name='Pro', price=249, requests=30000)
    ...


if __name__ == '__main__':
    setup()
    #countries()
