# -*- coding: utf-8 -*-
"""
Get weather in console.

# http://rss.accuweather.com/rss/liveweather_rss.asp?metric=1&locCode=<state%20name>|<city>
# http://rss.accuweather.com/rss/liveweather_rss.asp?metric=1&locCode=<postal_code>
# Find location by IP:
# > curl -X GET "http://dataservice.accuweather.com/locations/v1/cities/ipaddress?apikey=<apikey>q=<ip_address>"
# http://api.wunderground.com/api/<apikey>/conditions/q/11767.json

Date: 2016-11-29
Author: Maksim Rakitin
"""

import json
import netrc
import os

import requests

URL_IP = 'http://ipinfo.io'

server = 'accu'  # 'wund'
if server == 'accu':
    WEATHER_SERVER = 'dataservice.accuweather.com'
    URL_IP2GEO = 'http://{}/locations/v1/cities/ipaddress'.format(WEATHER_SERVER)
    URL_POSTAL = 'http://{}/locations/v1/postalcodes/search'.format(WEATHER_SERVER)
    URL_COND = 'http://{}/currentconditions/v1/{}'.format(WEATHER_SERVER, {})
elif server == 'wund':
    WEATHER_SERVER = 'api.wunderground.com'
    URL_COND = 'http://{}/api/{}/conditions/q/{}.json'.format(WEATHER_SERVER, {}, {})
else:
    raise ValueError('Server <{}> is not supported.'.format(server))

def get_city_by_ip(ip):
    # Get the location key from the IP address:
    payload_location = _update_dict({'q': ip})
    r = requests.get(URL_IP2GEO, payload_location)
    data_location = json.loads(r.text)
    _check_status_code(r.status_code, data_location)
    return data_location


def get_city_by_postal(postal):
    # Get the location key from the postal code:
    payload_postal = _update_dict({'q': postal})
    r = requests.get(URL_POSTAL, payload_postal)
    data_postal = json.loads(r.text)
    _check_status_code(r.status_code, data_postal)
    for rec in data_postal:
        if rec['PrimaryPostalCode'] == postal:
            return rec
    raise ValueError('Location not found: {}'.format(postal))


def get_current_conditions(location_key, details=True):
    # Get current conditions:
    payload_conditions = _update_dict({'details': details})
    r = requests.get(URL_COND.format(location_key), payload_conditions)
    data_conditions = json.loads(r.text)
    _check_status_code(r.status_code, data_conditions)
    return data_conditions

def get_current_conditions_wund(postal, apikey):
    # Get current conditions:
    payload_conditions = {}
    r = requests.get(URL_COND.format(apikey, postal), payload_conditions)
    data_conditions = json.loads(r.text)
    _check_status_code(r.status_code, data_conditions)
    return data_conditions

def get_external_ip():
    # Get the external IP:
    r = requests.get(URL_IP)
    data_ip = json.loads(r.text)
    _check_status_code(r.status_code, data_ip)
    return data_ip


def _check_status_code(code, data):
    if code != 200:
        code_text = 'Code [{}]'.format(code)
        try:
            msg = '{} - {}: {}'.format(code_text, data['Code'], data['Message'])
        except:
            msg = '{} - {}'.format(code_text, ', '.join(data.values()))
        raise ValueError(msg)


def _get_api_key():
    if not os.environ.get('HOME'):
        os.environ.setdefault('HOME', os.environ.get('userprofile'))
    return netrc.netrc().hosts[WEATHER_SERVER][2]


def _print_weather(weather_icon, city, state, postal, cond):
    print(u'Weather in {}, {} {}: {}°{} - {}{}'.format(
        city, state, postal,
        cond['Temperature']['Metric']['Value'], cond['Temperature']['Metric']['Unit'],
        weather_icon, cond['WeatherText'],
    ))


def _update_dict(d):
    d['apikey'] = _get_api_key()
    return d


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Get weather in console')
    parser.add_argument('-p', '--postal', dest='postal', help='get weather for the provided postal code')
    parser.add_argument('-i', '--use-ip', dest='use_ip', action='store_true',
                        help='use IP address to get the weather instead of postal code')
    parser.add_argument('-n', '--no-details', dest='details', action='store_false',
                        help='do not get detailed conditions')

    args = parser.parse_args()

    if args.postal:
        postal = args.postal
        if server == 'accu':
            location = get_city_by_postal(postal)
            city = location['EnglishName']
            state = location['AdministrativeArea']['ID']
        else:
            apikey = _get_api_key()
            location = get_current_conditions_wund(postal, apikey)
    else:
        ip_info = get_external_ip()
        if args.use_ip:
            location = get_city_by_ip(ip_info['ip'])
        else:
            # It's more reliable to determine location by a postal code rather than by IP:
            location = get_city_by_postal(ip_info['postal'])
        city = location['EnglishName']
        state = location['AdministrativeArea']['ID']
        postal = location['PrimaryPostalCode']

    conditions = get_current_conditions(location['Key'], args.details)
    weather_icons = {
        1: u'⛭',  # Sunny
        2: u'⛭☁',  # Mostly Sunny
        3: u'☼☁',  # Partly Sunny
        4: u'⛅',  # Intermittent Clouds
        5: u'⛅☁',  # Hazy Sunshine
        6: u'☁⛅',  # Mostly Cloudy
        7: u'☁',  # Cloudy
        8: u'@☁',  # Dreary (Overcast)
        11: u'🌫',  # Fog
        12: u'☂⛆︎',  # Showers
        13: u'☁⛅⛆☂︎',  # Mostly Cloudy w/ Showers
        14: u'⛅☁⛆☂',  # Partly Sunny w/ Showers
        15: u'☁⚡⛈⛆☂',  # T-Storms
        16: u'☁⛅⚡⛈⛆☂',  # Mostly Cloudy w/ T-Storms
        17: u'⛅☁⚡⛈⛆☂',  # Partly Sunny w/ T-Storms
        18: u'☁⛆☂',  # Rain
    }

    try:
        weather_icon = '' if conditions[0]['WeatherIcon'] not in weather_icons.keys() else '{} '.format(
            weather_icons[conditions[0]['WeatherIcon']])
        _print_weather(weather_icon, city, state, postal, conditions[0])
    except UnicodeEncodeError:
        _print_weather('', city, state, postal, conditions[0])
