# stdlib
import json
import logging
import requests
import time

# project
from utils import (
    approx_time_elapsed, meters_to_miles, seconds_breakdown, time_since
)

log = logging.getLogger(__name__)


class RunKeeperAPI(object):
    API_URL = 'https://api.runkeeper.com'
    ACTIVITIES_URL = '%s/fitnessActivities' % API_URL
    CONTENT_TYPE = 'application/vnd.com.runkeeper.FitnessActivityFeed+json'
    TS_PATTERN = '%a, %d %b %Y %H:%M:%S'

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def __init__(self):
        # TODO: Use oauth?
        # TODO: Load via KMS
        self.ACCESS_TOKEN = ''

    def fetch_details(self):
        activity_uri = self.last_activity_uri()
        url = '%s%s?access_token=%s' % (
            self.API_URL, activity_uri, self.ACCESS_TOKEN
        )
        r = requests.get(url, headers={'Content-Type': self.CONTENT_TYPE})
        activity = json.loads(r.content)
        activity_ts = activity.get('start_time', '')
        time_elapsed = self.time_since(activity_ts)
        activity_type = activity.get('type', '')
        duration = seconds_breakdown(activity.get('duration', 0))

        return {
            'time_elapsed': time_elapsed,
            'rough_time_elapsed': approx_time_elapsed(time_elapsed),
            'type': activity_type,
            'duration': self.normalize_duration(duration),
            'total_calories': 0,  # TODO: Add this!
            'total_miles': meters_to_miles(activity.get('total_distance', 0)),
            'num_activity_words': len(activity_type.split(' '))
        }

    def normalize_duration(self, duration):
        if not duration.get('hours'):
            duration['hours'] = 0

        # Format for nice visual presentation
        duration['hours'] = "%02d" % duration['hours']
        duration['minutes'] = "%02d" % duration['minutes']
        duration['seconds'] = "%02d" % duration['seconds']

        return duration

    def last_activity_uri(self):
        url = '%s?access_token=%s' % (self.ACTIVITIES_URL, self.ACCESS_TOKEN)
        r = requests.get(url, headers={'Content-Type': self.CONTENT_TYPE})
        content = json.loads(r.content)
        activities = content.get('items', [])
        return activities[0].get('uri', '') if len(activities) else ''

    def time_since(self, ts_str):
        # TODO: Use regex
        temp_ts_str = ts_str.split(' ')
        if len(temp_ts_str) == 1 and '0' not in temp_ts_str:
            temp_ts_str[1] = '0' + temp_ts_str[1]
        ts_str = " ".join(temp_ts_str)

        unix_tstmp = time.mktime(time.strptime(ts_str, self.TS_PATTERN))
        return time_since(unix_tstmp)
