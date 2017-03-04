# stdlib
from config import get_base_config

import json
import logging
import requests

log = logging.getLogger(__name__)
config = get_base_config()


class WundergroundAPI(object):
    API_URL = 'http://api.wunderground.com/api'

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def __init__(self):
        # TODO: Load via KMS
        self.ACCESS_TOKEN = config.get('api', 'wunderground_key')

    def current_temp(self, location):
        # TODO Limited to 500 calls per day, so let's not waste it!
        city, state_abv = location.split(',')
        city = city.replace(' ', '_')
        url = '%s/%s/conditions/q/%s/%s.json' % (
            self.API_URL, self.ACCESS_TOKEN, state_abv, city
        )
        r = requests.get(url)
        weather = json.loads(r.content)
        return weather.get('current_observation', {}).get('temp_f', 'ERR')
