# stdlib
from bs4 import BeautifulSoup

import logging
import requests

log = logging.getLogger(__name__)


class MyFitnessPalAPI(object):
    API_URL = 'http://www.myfitnesspal.com/food/diary/JohnLZeller'

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def fetch_details(self):
        # Very hacky right now. Applied for API access. Waiting to hear back.
        r = requests.get(self.API_URL)
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
