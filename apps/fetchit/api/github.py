#!/usr/bin/env python

# stdlib
from bs4 import BeautifulSoup

import json
import logging
import re
import requests


# project
from utils import (
    approx_time_elapsed, get_conf, time_since, time_to_local_epoch
)


# TODO: Does this actually work with just string and not logging.INFO?
# TODO: Move to utils or something
logging.basicConfig(
    filename=get_conf('main', 'log_file', 'fetchit.log'),
    level=get_conf('main', 'log_level', logging.INFO)
)
log = logging.getLogger(__name__)


class GithubAPI(object):
    API_URL = 'https://api.github.com/users/JohnLZeller'
    EVENTS_URL = '%s/events' % API_URL
    CONTRIB_PATTERN = r'(\s+)(\d+)(\scontributions)'
    FILETYPE_PATTERN = r'.*(\.\w+)'

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def __init__(self):
        # TODO: Use oauth?
        # TODO: Load via KMS
        self.ACCESS_TOKEN = ''

    def fetch_details(self):
        push = self.last_push()
        if not push:
            return None

        repo_name = push.get('repo', {}).get('name')
        created_at = time_to_local_epoch(push.get('created_at'))
        commits = push.get('payload', {}).get('commits', [])
        commit = commits[0] if commits else {}  # Most recent commit
        commit_data = self.get_commit_data(commit)
        time_elapsed = time_since(created_at)

        details = {
            'created_at': created_at,
            'time_elapsed': time_elapsed,
            'rough_time_elapsed': approx_time_elapsed(time_elapsed),
            'repo': repo_name.split('/')[-1],  # TODO: Use a regex
            'repo_url': 'https://github.com/%s' % repo_name,
            'type': push.get('type', '').strip('Event'),
            'url': commit_data.get('html_url', ''),  # human readable URL
            'avatar_url': push.get('actor', {}).get('avatar_url', ''),
            'location': self.get_location(),
            'total_commits': self.total_commits(),
            'file_types_str': self.file_types(commit_data)
        }

        return details

    def last_push(self):
        # TODO: Fetch other types of events also
        event_type = 'PushEvent'
        per_page = 100
        url = '%s?access_token=%s&per_page=%s' % (
            self.EVENTS_URL, self.ACCESS_TOKEN, per_page
        )
        r = requests.get(url)
        events = json.loads(r.content)
        for event in events:
            if event.get('type', '') == event_type:
                return event
        return None

    def get_commit_data(self, commit):
        url = commit.get('url', '')
        if url:
            r = requests.get(url)
            return json.loads(r.content)
        return {}

    def get_location(self):
        # TODO: Use Google's location history by looking at the kml dumps here
        #       https://maps.google.com/locationhistory/b/0/kml?startTime=1373666400000&endTime=1373752800000
        url = '%s?access_token=%s' % (self.API_URL, self.ACCESS_TOKEN)
        r = requests.get(url)
        profile = json.loads(r.content)
        return profile.get('location', 'New York, NY')  # TODO: Default?

    def total_commits(self):
        r = requests.get('https://github.com/JohnLZeller')
        github_page = BeautifulSoup(r.content)
        contrib_graph = github_page.find_all(
            'div', {'class', 'js-contribution-graph'}
        )
        contribs = contrib_graph[0].find_all('h2')
        contrib_text = contribs[0].string
        match = re.match(self.CONTRIB_PATTERN, contrib_text)

        return match.group(2) if match else None

    def file_types(self, commit_data):
        file_types = []

        for f in commit_data.get('files', ''):
            match = re.match(self.FILETYPE_PATTERN, f.get('filename', ''))
            f = match.group(1) if match else ''
            if f not in file_types:
                file_types.append(f)

        return ', '.join(set(file_types))
