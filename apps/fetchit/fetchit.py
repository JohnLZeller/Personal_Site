#!/usr/bin/env python

# stdlib
import json
import logging
import requests
import time

from bs4 import BeautifulSoup

# project
from api.github import GithubAPI
from utils import (
    approx_time_elapsed, get_conf, meters_to_miles,
    seconds_breakdown, time_since
)


RK_ACCESS_TOKEN = ''
WEATHER_ACCESS_TOKEN = ''

DEFAULT_PERIOD = 300
WEATHER_API = 'http://api.wunderground.com/api'
MFP_API = 'http://www.myfitnesspal.com/food/diary/JohnLZeller'
RUNKEEPER_API = 'https://api.runkeeper.com'  # TODO: Call it RK
RUNKEEPER_ACTIVITIES = '%s/fitnessActivities' % RUNKEEPER_API
RUNKEEPER_CONTENT_TYPE = 'application/vnd.com.runkeeper.FitnessActivityFeed+json'
RUNKEEPER_TS_PATTER = '%a, %d %b %Y %H:%M:%S'

# TODO: Does this actually work with just string and not logging.INFO?
logging.basicConfig(
    filename=get_conf('main', 'log_file', 'fetchit.log'),
    level=get_conf('main', 'log_level', logging.INFO)
)
log = logging.getLogger(__name__)

def current_temp(location):
    # TODO Limited to 500 calls per day, so let's not waste it!
    city, state_abv = location.split(',')
    city = city.replace(' ', '_')
    url = '%s/%s/conditions/q/%s/%s.json' % (
        WEATHER_API, WEATHER_ACCESS_TOKEN, state_abv, city
    )
    r = requests.get(url)
    weather = json.loads(r.content)
    return weather.get('current_observation', {}).get('temp_f', 'ERR')

def fetch_nurtrition_details():
    # Very hacky at the moment. Applied for API access. Waiting to hear back
    r = requests.get(MFP_API)
    soup = BeautifulSoup(r.content)
    total_class = soup.find('tr', {'class', 'total'})
    info = {
        'calories_eaten': total_class.td.next_sibling.next_sibling.string,
        'coffees': 0
    }

    # Find all coffees
    foods = soup.find_all('td', {'class', 'first'})
    for food in foods:
        if food.string in ['coffee', 'Coffee', 'espresso', 'Espresso']:
            info['coffees'] += 1

    return info

def get_most_recent_fitness_activity_uri():
    url = '%s?access_token=%s' % (RUNKEEPER_ACTIVITIES, RK_ACCESS_TOKEN)
    r = requests.get(url, headers={'Content-Type': RUNKEEPER_CONTENT_TYPE})
    content = json.loads(r.content)
    activities = content.get('items', [])
    return activities[0].get('uri', '') if len(activities) else ''

def fetch_fitness_details():
    activity_uri = get_most_recent_fitness_activity_uri()
    url = '%s%s?access_token=%s' % (
        RUNKEEPER_API, activity_uri, RK_ACCESS_TOKEN
    )
    r = requests.get(url, headers={'Content-Type': RUNKEEPER_CONTENT_TYPE})
    activity = json.loads(r.content)
    activity_ts = activity.get('start_time', '')
    time_elapsed = time_since_fitness_activity(activity_ts)
    activity_type = activity.get('type', '')

    return {
        'time_elapsed': time_elapsed,
        'rough_time_elapsed': approx_time_elapsed(time_elapsed),  # TODO: '%s Ago'?
        'type': activity_type,
        'duration': seconds_breakdown(activity.get('duration', 0)),
        'total_miles': meters_to_miles(activity.get('total_distance', 0)),
        'num_activity_words': len(activity_type.split(' '))
    }

def time_since_fitness_activity(ts_str):
    # TODO: Use regex
    temp_ts_str = ts_str.split(' ')
    if len(temp_ts_str) == 1 and '0' not in temp_ts_str:
        temp_ts_str[1] = '0' + temp_ts_str[1]
    ts_str = " ".join(temp_ts_str)

    unix_tstmp = time.mktime(time.strptime(ts_str, RUNKEEPER_TS_PATTER))
    return time_since(unix_tstmp)

def main():
    log.info("Starting up main loop execution...")
    gh_api = GithubAPI()
    while 1:
        gh_details = gh_api.fetch_details()
        print gh_details
        print current_temp(gh_details['location'])
        print fetch_fitness_details()
        print fetch_nurtrition_details()
        # TODO: Catch CTRL-C or CTRL-Z and do some cleanup

        time.sleep(float(get_conf('main', 'period', DEFAULT_PERIOD)))

    log.info("Shutting down...")

if __name__ == '__main__':
    main()
