#!/usr/bin/env python
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from flask.ext.mail import Mail, Message

import time
import urllib2
import json
import xmltodict
import os
import requests
import re
import pytz

from forms import ContactForm
from pprint import pprint
from datetime import datetime
from bs4 import BeautifulSoup


## SETUP
DEBUG = False
SECRET_KEY = ''
USERNAME = ''
PASSWORD = ''
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
RK_ACCESS_TOKEN = ''
WEATHER_ACCESS_TOKEN = ''
DB_USERNAME = ''
DB_PASSWORD = ''
DB_DATABASE = ''
CSRF_ENABLED = False # TODO: Add CSRF Protection :)

# Setup app
application = Flask(__name__)
app = application

# Connect to blog database
try:
    engine = create_engine('mysql://{}:{}@localhost/{}?charset=utf8&'.format(DB_USERNAME, DB_PASSWORD, DB_DATABASE), convert_unicode=True, echo=False)
    Base = declarative_base()
    Base.metadata.reflect(engine)
    db_session = scoped_session(sessionmaker(bind=engine))

    class Posts(Base):
        __table__ = Base.metadata.tables['wp_posts']

    class Terms(Base):
        __table__ = Base.metadata.tables['wp_terms']

    class Term_Taxonomy(Base):
        __table__ = Base.metadata.tables['wp_term_taxonomy']

    class Term_Relationships(Base):
        __table__ = Base.metadata.tables['wp_term_relationships']
except Exception as e:
    print e

# Setup Mail
app.config.from_object(__name__)
mail = Mail(application)

### Tools ###
def most_recent_github_commit():
    try:
        commit = json.loads(requests.get('https://api.github.com/users/JohnLZeller/events').content)[0]
        details = {'created_at': datetime.strptime(commit['created_at'], '%Y-%m-%dT%H:%M:%SZ'),
                   'url': commit['payload']['commits'][0]['url'],
                   'repo': commit['repo']['name'].split('/')[-1],
                   'repo_url': 'https://github.com/{}'.format(commit['repo']['name']),
                   'type': re.sub(r'([a-z])([A-Z])', r'\1 \2', commit['type'].strip('Event'))}
        details['created_at'] = int(pytz.utc.localize(details['created_at']).astimezone(pytz.timezone('US/Pacific')).strftime("%s"))
        details['time_elapsed'] = int(datetime.now(tz=pytz.timezone('US/Pacific')).strftime("%s")) - details['created_at']

        # Grab Commit human readable URL
        commit_data = json.loads(requests.get(details['url']).content)
        details['url'] = commit_data['html_url']

        # Come up with the breakdown of time elapsed
        elapsed = {}
        elapsed['weeks'] = int(details['time_elapsed'] / 60 / 60 / 24 / 7)
        left = details['time_elapsed'] - (elapsed['weeks'] * 7 * 24 * 60 * 60)
        elapsed['days'] = int(left / 60 / 60 / 24)
        left = left - (elapsed['days'] * 24 * 60 * 60)
        elapsed['hours'] = int(left / 60 / 60)
        left = left - (elapsed['hours'] * 60 * 60)
        elapsed['minutes'] = int(left / 60)
        left = left - (elapsed['minutes'] * 60)
        elapsed['seconds'] = int(left)
        details['time_elapsed'] = elapsed

        # Come up with rough time elapsed
        for period in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
            if details['time_elapsed'][period] > 0:
                details['rough_time_elapsed'] = "{} {}".format(details['time_elapsed'][period], period.title())
                break

        # Grab avatar URL
        user = json.loads(requests.get('https://api.github.com/users/JohnLZeller').content)
        details['avatar_url'] = user['avatar_url']

        # Grab location in profile
        # TODO: This is a temporary fix until setting up the use of Google;s location history by looking at the kml dumps here 
        #       https://maps.google.com/locationhistory/b/0/kml?startTime=1373666400000&endTime=1373752800000
        profile = json.loads(requests.get('https://api.github.com/users/JohnLZeller').content)
        details['location'] = profile['location']

        # Grab total commits this year, longest streak and current streak
        github_page = requests.get('https://github.com/JohnLZeller').content
        github_page = BeautifulSoup(github_page)
        contrib_number_set = github_page.find_all('span', {'class', 'contrib-number'})
        details['total_commits_year'] = contrib_number_set[0].string.split(' total')[0]
        details['longest_streak'] = contrib_number_set[1].string.title()
        details['current_streak'] = contrib_number_set[2].string.title()

        # Grab file types
        files = commit_data['files']
        details['file_types'] = ''
        for f in files:
            if '.' in f['filename']:
                f = f['filename'].split('.')[1]
            else:
                f = f['filename']
            if f not in details['file_types']:
                details['file_types'] += '.{}, '.format(f)
        details['file_types'] = details['file_types'][:-2]
    except Exception as e:
        print e
        details = {'created_at': '',
                   'url': '',
                   'repo': '',
                   'repo_url': '',
                   'type': '',
                   'url': '',
                   'time_elapsed': {'weeks': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0},
                   'rough_time_elapsed': '',
                   'avatar_url': '',
                   'location': '',
                   'total_commits_year': '',
                   'longest_streak': '',
                   'current_streak': '',
                   'file_types': ''}

    return details

def current_temp(location):
    try:
        city, state_abv = location.split(',')
    except Exception as e:
        print e
        city, state_abv = ('Corvallis', 'OR')

    if ' ' in city:
        city = '_'.join(city.split(' '))
    try:
        weather = json.loads(requests.get('http://api.wunderground.com/api/{}/conditions/q/{}/{}.json'.format(WEATHER_ACCESS_TOKEN, state_abv, city)).content)
    except Exception as e:
        print e
        weather = 'ERR'
    return weather['current_observation']['temp_f']

def nutrition_info():
    try:
        # This is very hacky at the moment. Applied for API access and am waiting to hear back
        mfp = requests.get('http://www.myfitnesspal.com/food/diary/JohnLZeller').content
        soup = BeautifulSoup(mfp)
        info = {'calories_eaten': soup.find('tr', {'class', 'total'}).td.next_sibling.next_sibling.string,
                'coffees': 0}

        # Find all coffees
        foods = soup.find_all('td', {'class', 'first'})
        for food in foods:
            try:
                if 'coffee' in food.string or 'Coffee' in food.string or \
                   'espresso' in food.string or 'Espresso' in food.string:
                    info['coffees'] += 1
            except TypeError:
                pass
    except Exception as e:
        print e
        info = {'calories_eaten': 0, 'coffees': 0}

    return info

def send_email(form):
    msg = Message(
       subject='CONTACT ME: ' + form.name.data,
       sender=form.email.data,
       recipients=['johnlzeller@gmail.com'])
    msg.body = form.message.data
    try:
        mail.send(msg)
    except Exception as e:
        print e
        form.success = False
        return form
    form.success = True
    
    return form

def get_fitness_activities():
    try:
        r = requests.get('https://api.runkeeper.com/fitnessActivities?access_token={}'.format(RK_ACCESS_TOKEN), 
                         headers={'Content-Type': 'application/vnd.com.runkeeper.FitnessActivityFeed+json'})
        activities = json.loads(r.content)
    except Exception as e:
        activities = {}
    return json.loads(r.content)

def most_recent_fitness_activity():
    try:
        activities = get_fitness_activities()
        activity = activities['items'][0]
        activity = requests.get('https://api.runkeeper.com{}?access_token={}'.format(activity['uri'], RK_ACCESS_TOKEN), 
                         headers={'Content-Type': 'application/vnd.com.runkeeper.FitnessActivityFeed+json'})
        activity = json.loads(activity.content)
        activity['time_elapsed'] = time_elapsed_since_fitness_activity(activity)
        activity['rough_time_elapsed'] = rough_time_elapsed(activity)

        duration = activity['duration']
        activity['duration'] = {'hours': duration / 60 / 60}
        activity['duration']['minutes'] = (duration - (activity['duration']['hours'] * 60 * 60)) / 60
        activity['duration']['seconds'] = duration - (activity['duration']['minutes'] * 60) - (activity['duration']['hours'] * 60 * 60)
        activity['duration']['hours'] = ("%02d" % activity['duration']['hours'])
        activity['duration']['minutes'] = ("%02d" % activity['duration']['minutes'])
        activity['duration']['seconds'] = ("%02d" % activity['duration']['seconds'])

        activity['total_distance'] = meters_to_miles(activity['total_distance'])

        activity['num_activity_words'] = len(activity['type'].split(' '))
    except Exception as e:
        print e
        activity = {'time_elapsed': '',
                    'rough_time_elapsed': '',
                    'duration': {'hours': 0, 'minutes': 0, 'seconds': 0},
                    'total_distance': 0,
                    'num_activity_words': 0}
    return activity

def time_elapsed_since_fitness_activity(activity):
    try:
        temp_tstmp = activity['start_time'].split(' ')
        if len(temp_tstmp) == 1 and '0' not in temp_tstmp:
            temp_tstmp[1] = '0'+temp_tstmp[1]
        tstmp = " ".join(temp_tstmp)

        unix_tstmp = time.mktime(time.strptime(tstmp, '%a, %d %b %Y %H:%M:%S'))
        since = time.time() - unix_tstmp

        elapsed = {}
        elapsed['weeks'] = int(since / 60 / 60 / 24 / 7)
        left = since - (elapsed['weeks'] * 7 * 24 * 60 * 60)
        elapsed['days'] = int(left / 60 / 60 / 24)
        left = since - (elapsed['days'] * 24 * 60 * 60)
        elapsed['hours'] = int(left / 60 / 60)
        left = since - (elapsed['hours'] * 60 * 60)
        elapsed['minutes'] = int(left / 60)
        left = since - (elapsed['minutes'] * 60)
        elapsed['seconds'] = int(left)
    except Exception as e:
        print e
        elapsed = {'weeks': 0, 'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
    return elapsed

def rough_time_elapsed(activity):
    elapsed = time_elapsed_since_fitness_activity(activity)

    for period in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
        if elapsed[period] > 0:
            return "{} {} Ago".format(elapsed[period], period.title())

def meters_to_miles(meters):
    return round(meters * 0.00062137, 2)

def grab_posts(category=None, number=None):
    posts = []
    try:
        # TODO: Order by most recent first
        if category:
            # TODO: Check that tax_id in the Term_Taxonomy table is referring to a 'category' by looking at 
            #       the taxonomy Column, if it is not, then the tax_id is wrong and probably referring to a tag
            term_id = db_session.query(Terms.term_id).filter_by(name=category.title()).first()
            tax_id = db_session.query(Term_Taxonomy.term_taxonomy_id).filter_by(term_id=int(term_id[0])).first()
            for obj_id in db_session.query(Term_Relationships.object_id).filter_by(term_taxonomy_id=int(tax_id[0])):
                for post in db_session.query(Posts.post_title, Posts.post_date, Posts.post_content, Posts.post_name).\
                                       filter_by(ID=int(obj_id[0]), post_status=u'publish'):
                    title, date, content, post_name = post
                    content_short = BeautifulSoup(content).find('p').text
                    posts.append({'title': title, 'date': date, 'post_name': post_name,
                                  'content': content,'content_short': content_short})
        else:
            for post in db_session.query(Posts.post_title, Posts.post_date, \
                                         Posts.post_content, Posts.post_name).\
                                   filter_by(post_status=u'publish'):
                content_short = BeautifulSoup(content).find('p').text
                title, date, content, post_name = post
                posts.append({'title': title, 'date': date, 'content': content, 
                              'post_name': post_name, 'content_short': content_short})
    except Exception as e:
        print e
    
    return posts[0:number]

### Routing ###
@app.route('/', methods = ['GET'])
def home():
    form = ContactForm()
    if form.validate_on_submit():
        form = send_email(form)
    commit = most_recent_github_commit()
    return render_template('index.html', form = form, fitness = most_recent_fitness_activity(),
                                         commit = commit, 
                                         current_temp = current_temp(commit['location']),
                                         nutrition_info = nutrition_info(), 
                                         software_projects = grab_posts('Software Projects', 3),
                                         nonsoftware_projects = grab_posts('NonSoftware Projects', 3))

if __name__ == '__main__':
    # TODO: Add logging
    app.run()
