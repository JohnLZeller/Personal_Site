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
import pywapi
import pytz

from forms import ContactForm
from pprint import pprint
from datetime import datetime
from bs4 import BeautifulSoup


## SETUP
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_TLS = False
MAIL_USE_SSL= True
f = open('secret', 'r')
secrets = json.loads(f.read())
f.close()
MAIL_USERNAME = secrets['username']
MAIL_PASSWORD = secrets['password']
RK_ACCESS_TOKEN = secrets['acccess_token']
CSRF_ENABLED = False # TODO: Add CSRF Protection :)

# Setup app
application = Flask(__name__)
app = application
app.config['SECRET_KEY'] = "deterministic"
app.config['TESTING'] = True

# Connect to blog database
#engine = create_engine('sqlite:///blog/content/data/ghost-dev.db', convert_unicode=True, echo=False)
#Base = declarative_base()
#Base.metadata.reflect(engine)
#db_session = scoped_session(sessionmaker(bind=engine))

#class Posts(Base):
#    __table__ = Base.metadata.tables['posts']

#class Settings(Base):
#    __table__ = Base.metadata.tables['settings']

# Setup Mail
app.config.from_object(__name__)
mail = Mail(application)

### Tools ###
def most_recent_github_commit():
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
        f = f['filename'].split('.')[1]
        if f not in details['file_types']:
            details['file_types'] += '.{}, '.format(f)
    details['file_types'] = details['file_types'][:-2]

    return details

def mozilla_hg_commits():
    # changes structure = [timestamp, eventtype, description, revision, event_url, repo_name, repo_url]
    # Dictionaries for reference
    tzones = {"-05:00": 10800.0, "-06:00": 10800.0, "-07:00": 0.0, "-08:00": 0.0} # Only adjust to EST, not CST or MST

    # User Repos
    hg_repos = BeautifulSoup(urllib2.urlopen("http://hg.mozilla.org/users/jozeller_mozilla.com/").read()).find('table').find_all('tr')[1:]
    hg_repo_urls = []
    for repo in hg_repos:
        hg_repo_urls.append("http://hg.mozilla.org" + str(repo.find_all('a', href=True)[0]['href']) + "atom-feed")
    hg = []
    hg_changes = []
    for url in hg_repo_urls:
        try:
            d = urllib2.urlopen(url).read()
        except urllib2.HTTPError as e:
            app.logger.error(str(e) + " when attempting to open " + str(url))
            continue
        d = xmltodict.parse(d)
        hg.append(d['feed']['entry'])
    for repo in hg:
        for entry in repo:
            tz = str(entry['published'])[-6:]
            t = str(entry['published']).split(tz)[0]
            t = int(time.mktime(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").timetuple()) - tzones[tz])
            repo_name = str(entry['link']['@href']).split("http://hg.mozilla.org")[1].split("rev/")[0]
            repo_url = str(entry['link']['@href']).split("rev/")[0]
            rev = str(entry['link']['@href']).split("http://hg.mozilla.org")[1].split("rev/")[1]
            hg_changes.append([str(t), "PushEvent", str(entry['title']), rev, str(entry['link']['@href']), repo_name, repo_url])

    # BuildAPI
    entries = []
    try:
        d = urllib2.urlopen("http://hg.mozilla.org/build/buildapi/atom-feed").read()
    except urllib2.HTTPError as e:
        app.logger.error(str(e) + " when attempting to open " + str(url))
    finally:
        d = xmltodict.parse(d)
        entries.append(d['feed']['entry'])
        for entry in entries[0]:
            if entry['author']['name'] == "John Zeller":
                tz = str(entry['published'])[-6:]
                t = str(entry['published']).split(tz)[0]
                t = int(time.mktime(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").timetuple()) - tzones[tz])
                repo_name = str(entry['link']['@href']).split("http://hg.mozilla.org")[1].split("rev/")[0]
                repo_url = str(entry['link']['@href']).split("rev/")[0]
                rev = str(entry['link']['@href']).split("http://hg.mozilla.org")[1].split("rev/")[1]
                hg_changes.append([str(t), "PushEvent", str(entry['title']), rev, str(entry['link']['@href']), repo_name, repo_url])

    hg_changes = reversed(sorted(hg_changes))

    return list(hg_changes)

def current_temp(location):
    # TODO: Can be improved to take zip code instead
    city, state_abv = location.split(', ')
    location_ids = pywapi.get_location_ids(city)
    for i, c in location_ids.items():
        if c == location:
            location_id = i
            break
    weather = pywapi.get_weather_from_weather_com(location_id)
    temperature_f = round(int(weather['current_conditions']['temperature']) * (9.0/5.0) + 32, 2)
    return temperature_f

def nutrition_info():
    # This is very hacky at the moment. Applied for API access and am waiting to hear back
    mfp = requests.get('http://www.myfitnesspal.com/food/diary/JohnLZeller').content
    soup = BeautifulSoup(mfp)
    info = {'calories_eaten': soup.find('tr', {'class', 'total'}).td.next_sibling.next_sibling.string,
            'coffees': 0}#mfp.split('<td class="first">Totals</td>')[1].split('<td>')[1].split('</td>')[0]}

    # Find all coffees
    foods = soup.find_all('td', {'class', 'first'})
    for food in foods:
        try:
            if 'coffee' in food.string or 'Coffee' in food.string or \
               'espresso' in food.string or 'Espresso' in food.string:
                info['coffees'] += 1
        except TypeError:
            pass

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
    r = requests.get('https://api.runkeeper.com/fitnessActivities?access_token={}'.format(RK_ACCESS_TOKEN), 
                     headers={'Content-Type': 'application/vnd.com.runkeeper.FitnessActivityFeed+json'})
    return json.loads(r.content)

def most_recent_fitness_activity():
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
    return activity

def time_elapsed_since_fitness_activity(activity):
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
    return elapsed

def rough_time_elapsed(activity):
    elapsed = time_elapsed_since_fitness_activity(activity)

    for period in ['weeks', 'days', 'hours', 'minutes', 'seconds']:
        if elapsed[period] > 0:
            return "{} {} Ago".format(elapsed[period], period.title())

def meters_to_miles(meters):
    return round(meters * 0.00062137, 2)

### Routing ###
@app.route('/', methods = ['GET', 'POST'])
def home():
    form = ContactForm()
    if form.validate_on_submit():
        form = send_email(form)
    commit = most_recent_github_commit()
    return render_template('index.html', form=form, fitness=most_recent_fitness_activity(),
                                         commit=most_recent_github_commit(), current_temp=current_temp(commit['location']),
                                         nutrition_info=nutrition_info())

@app.route('/git')
def show_most_recent_git_commit():
    return render_template('git.html', changes=most_recent_github_commit())

@app.route('/blog')
def redirect_to_blog():
    return redirect('http://blog.zwikle.com')

@app.route('/blog-test')
def show_blog():
    posts = []
    for item in db_session.query(Posts.title, Posts.html, Posts.status):
        title, post, status = item
        if status == 'published':
            posts.append({'title': title, 'post': post})
    settings = {}
    for item in db_session.query(Settings.key, Settings.value):
        key, value = item
        if key == 'title':
            settings['title'] = value
        if key == 'description':
            settings['description'] = value

    return render_template('blog.html', posts=posts, settings=settings)

if __name__ == '__main__':
    #if not app.debug:
    import logging
    from logging.handlers import WatchedFileHandler
    file_handler = WatchedFileHandler('flask.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.WARNING)
    app.run()
