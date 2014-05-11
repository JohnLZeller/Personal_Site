from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import time
from flask.ext.sqlalchemy import SQLAlchemy
from pprint import pprint
from datetime import datetime
import urllib2
import json
from bs4 import BeautifulSoup
import xmltodict


## SETUP
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

application = Flask(__name__)
app = application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
db = SQLAlchemy(app)
app.config.from_object(__name__)

app.config['BROWSERID_LOGIN_URL'] = "/login"
app.config['BROWSERID_LOGOUT_URL'] = "/logout"
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

### Routing ###
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/repos')
def show_repos():
    return render_template('test.html', changes=repos())

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