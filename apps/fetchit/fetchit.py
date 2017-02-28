#!/usr/bin/env python

# stdlib
import logging
import time

# project
from api.github import GithubAPI
from api.myfitnesspal import MyFitnessPalAPI
from api.runkeeper import RunKeeperAPI
from api.wunderground import WundergroundAPI

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
    gh_api = GithubAPI()
    weather_api = WundergroundAPI()
    mfp_api = MyFitnessPalAPI()
    rk_api = RunKeeperAPI()
    while 1:
        gh_details = gh_api.fetch_details()
        print gh_details
        print weather_api.current_temp(gh_details['location'])
        print mfp_api.fetch_details()
        print rk_api.fetch_details()
        # TODO: Catch CTRL-C or CTRL-Z and do some cleanup

        time.sleep(float(get_conf('main', 'period', DEFAULT_PERIOD)))

    log.info("Shutting down...")

if __name__ == '__main__':
    main()
