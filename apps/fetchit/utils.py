# stdlib
import logging
from datetime import datetime

import pytz

CREATED_PATTERN = '%Y-%m-%dT%H:%M:%SZ'
PST_TZ = tz = pytz.timezone('US/Pacific')

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7

log = logging.getLogger(__name__)


def time_to_local_epoch(ts):
    # TODO: Make UTC. Why localized?
    ts = datetime.strptime(ts, CREATED_PATTERN)
    ts = pytz.utc.localize(ts).astimezone(PST_TZ).strftime("%s")
    return int(ts)


def now_local_epoch():
    return int(datetime.now(tz=PST_TZ).strftime("%s"))


def time_since(ts):
    return seconds_breakdown(now_local_epoch() - ts)


def seconds_breakdown(s):
    breakdown = {}

    if s >= WEEK:
        breakdown['weeks'] = int(s / 60 / 60 / 24 / 7)
        s = s - (breakdown['weeks'] * 7 * 24 * 60 * 60)

    if s >= DAY:
        breakdown['days'] = int(s / 60 / 60 / 24)
        s = s - (breakdown['days'] * 24 * 60 * 60)

    if s >= HOUR:
        breakdown['hours'] = int(s / 60 / 60)
        s = s - (breakdown['hours'] * 60 * 60)

    if s >= MINUTE:
        breakdown['minutes'] = int(s / 60)
        s = s - (breakdown['minutes'] * 60)

    breakdown['seconds'] = int(s)

    return breakdown


def approx_time_elapsed(time_elapsed):
    rough_time_elapsed = ""
    units = ['weeks', 'days', 'hours', 'minutes', 'seconds']
    units = [u for u in units if time_elapsed.get(u)]
    for unit in units:
        value = time_elapsed[unit]
        if value > 0:
            if value == 1:
                unit = unit[:-1]  # removes the 's' when value is singular
            rough_time_elapsed = "%s %s" % (time_elapsed[unit], unit.title())
            break
    return rough_time_elapsed


def meters_to_miles(meters):
    return round(meters * 0.00062137, 2)
