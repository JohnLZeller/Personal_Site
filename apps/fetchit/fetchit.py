#!/usr/bin/env python

# stdlib
import json
import logging
import requests
import time

from bs4 import BeautifulSoup

# project
from api.github import GithubAPI
from api.myfitnesspal import MyFitnessPalAPI
from api.wunderground import WundergroundAPI
from utils import (
    approx_time_elapsed, get_conf, meters_to_miles,
    seconds_breakdown, time_since
)


RK_ACCESS_TOKEN = ''

DEFAULT_PERIOD = 300
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
    weather_api = WundergroundAPI()
    mfp_api = MyFitnessPalAPI()
    while 1:
        gh_details = gh_api.fetch_details()
        print gh_details
        print weather_api.current_temp(gh_details['location'])
        print mfp_api.fetch_details()
        print fetch_fitness_details()
        # TODO: Catch CTRL-C or CTRL-Z and do some cleanup

        time.sleep(float(get_conf('main', 'period', DEFAULT_PERIOD)))

    log.info("Shutting down...")

if __name__ == '__main__':
    main()
