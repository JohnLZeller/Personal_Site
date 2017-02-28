#!/usr/bin/env python

# stdlib
import logging
import time

# project
from api.github import GithubAPI
from api.myfitnesspal import MyFitnessPalAPI
from api.runkeeper import RunKeeperAPI
from api.wunderground import WundergroundAPI

from cache import RedisCache

from utils import get_conf


DEFAULT_PERIOD = 300

# TODO: Does this actually work with just string and not logging.INFO?
# TODO: Move to utils or something
logging.basicConfig(
    filename=get_conf('main', 'log_file', 'fetchit.log'),
    level=get_conf('main', 'log_level', logging.INFO)
)
log = logging.getLogger(__name__)


def main():
    log.info("Starting up main loop execution...")
    conn = RedisCache()
    gh_api = GithubAPI()
    weather_api = WundergroundAPI()
    mfp_api = MyFitnessPalAPI()
    rk_api = RunKeeperAPI()

    import pdb; pdb.set_trace()
    # TODO: Get from cache, and pass to api class to replace not found data
    while 1:
        gh_details = gh_api.fetch_details()
        conn.set_json('github_data', gh_details)
        temp = weather_api.current_temp(gh_details['location'])
        conn.set_json('temp_f', temp)
        conn.set_json('myfitnesspal_data', mfp_api.fetch_details())
        conn.set_json('runkeeper_data', rk_api.fetch_details())
        log.info("Data cached successfully!")
        # TODO: Catch CTRL-C or CTRL-Z and do some cleanup

        time.sleep(float(get_conf('main', 'period', DEFAULT_PERIOD)))

    log.info("Shutting down...")

if __name__ == '__main__':
    main()
