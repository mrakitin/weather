# -*- coding: utf-8 -*-
"""
Get weather in console.

# http://rss.accuweather.com/rss/liveweather_rss.asp?metric=1&locCode=<state%20name>|<city>
# http://rss.accuweather.com/rss/liveweather_rss.asp?metric=1&locCode=<postal_code>
# Find location by IP:
# > curl -X GET "http://dataservice.accuweather.com/locations/v1/cities/ipaddress?apikey=<apikey>q=<ip_address>"

Date: 2016-11-29
Author: Maksim Rakitin
"""

import json
import netrc
import os

import requests

URL_IP = 'http://ipinfo.io'
WEATHER_SERVER = 'dataservice.accuweather.com'

URL_IP2GEO = 'http://{}/locations/v1/cities/ipaddress'.format(WEATHER_SERVER)
URL_COND = 'http://{}/currentconditions/v1/{}'.format(WEATHER_SERVER, {})
URL_POSTAL = 'http://{}/locations/v1/postalcodes/search'.format(WEATHER_SERVER)


def get_city_by_ip(ip):
    # Get the location key from the IP address:
    payload_location = _update_dict({'q': ip})
    r = requests.get(URL_IP2GEO, payload_location)
    data_location = json.loads(r.text)
    return data_location


def get_city_by_postal(postal):
    # Get the location key from the postal code:
    payload_postal = _update_dict({'q': postal})
    r = requests.get(URL_POSTAL, payload_postal)
    data_postal = json.loads(r.text)
    for r in data_postal:
        if r['PrimaryPostalCode'] == postal:
            my_location = r
            break
    return my_location


def get_current_conditions(location_key, details=True):
    # Get current conditions:
    payload_conditions = _update_dict({'details': details})
    r = requests.get(URL_COND.format(location_key), payload_conditions)
    data_conditions = json.loads(r.text)
    return data_conditions


def get_external_ip():
    # Get the external IP:
    r = requests.get(URL_IP)
    data_ip = json.loads(r.text)
    return data_ip


def _get_api_key():
    if not os.environ.get('HOME'):
        os.environ.setdefault('HOME', os.environ.get('userprofile'))
    return netrc.netrc().hosts[WEATHER_SERVER][2]


def _update_dict(d):
    d['apikey'] = _get_api_key()
    return d


if __name__ == '__main__':
    if_use_ip = False
    details = True

    # Get IP info (it's more reliable to determine location by this method rather than the automatic method by IP):
    ip_info = get_external_ip()
    location = get_city_by_ip(ip_info['ip']) if if_use_ip else get_city_by_postal(ip_info['postal'])
    conditions = get_current_conditions(location['Key'], details)
    weather_icons = {
        1: u'☼',
        2: u'☼',
        3: u'☼',
        4: u'☼',
        5: u'☼',
        6: u'☁',
        7: u'☁',
        8: u'☁',
        11: u'☁',
        12: u'☂',
        18: u'☔',
    }
    weather_icon = '' if conditions[0]['WeatherIcon'] not in weather_icons.keys() else '{} '.format(
        weather_icons[conditions[0]['WeatherIcon']])

    print(u'Weather in {}, {} {}: {}°{} - {}{}'.format(
        ip_info['city'], ip_info['region'], ip_info['postal'],
        conditions[0]['Temperature']['Metric']['Value'], conditions[0]['Temperature']['Metric']['Unit'],
        weather_icon, conditions[0]['WeatherText'],
    ))
