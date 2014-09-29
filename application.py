from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message

import time
import urllib2
import json
import xmltodict
import os
import requests

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
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
RK_ACCESS_TOKEN = os.environ.get('RK_ACCESS_TOKEN')
CSRF_ENABLED = False # TODO: Add CSRF Protection :)

application = Flask(__name__)
app = application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'

db = SQLAlchemy(app)
app.config.from_object(__name__)
mail = Mail(application)

app.config['SECRET_KEY'] = "deterministic"
app.config['TESTING'] = True

### Tools ###
def repos(): # changes structure = [timestamp, eventtype, description, revision, event_url, repo_name, repo_url]
	# Dictionaries for reference
	tzones = {"-05:00": 10800.0, "-06:00": 10800.0, "-07:00": 0.0, "-08:00": 0.0} # Only adjust to EST, not CST or MST

	# Github
	github = json.loads(urllib2.urlopen("https://github.com/JohnLZeller.json").read())
	github_changes = []
	for commit in github:
		created_at = commit['created_at']
		event_type = commit['type']
		repo_name = commit['repository']['name']
		repo_url = commit['repository']['url']
		push_description = commit['payload'].get("shas")
		if push_description is not None: # PushEvent
			push_url = commit['url']
			for push in push_description:
				tz = created_at[-6:]
				t = created_at.split(tz)[0]
				t = int(time.mktime(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").timetuple()))
				github_changes.append([str(t), event_type, push[2], push[0], push_url, repo_name, repo_url])
		else:
			tz = created_at[-6:]
			t = created_at.split(tz)[0]
			t = int(time.mktime(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S").timetuple()))
			github_changes.append([str(t), event_type, event_type, "", "", repo_name, repo_url])

	# HG - Users
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

	# HG - BuildAPI
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

	# Combine Repos
	changes = hg_changes + github_changes
	changes = reversed(sorted(changes))

	return list(changes)

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

### Routing ###
@app.route('/', methods = ['GET', 'POST'])
def home():
    form = ContactForm()
    if form.validate_on_submit():
        form = send_email(form)
    return render_template('index.html', form=form, fitness=most_recent_fitness_activity())

@app.route('/repos')
def show_repos():
    return render_template('test.html', changes=repos())

@app.route('/test')
def test():
    return render_template('test.html')

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
