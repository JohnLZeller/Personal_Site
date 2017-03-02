#!/usr/bin/env python
from ConfigParser import NoOptionError, NoSectionError, SafeConfigParser

from flask import Flask, render_template
from flask.ext.mail import Mail, Message

from forms import ContactForm

import json
import logging
import redis


application = Flask(__name__)
app = application

config = SafeConfigParser()
config.read('config.ini')

# TODO: Does this actually work with just string and not logging.INFO?
# TODO: Move to utils or something
logging.basicConfig(
    filename=config.get('main', 'log_file'),
    level=config.get('main', 'log_level')
)
log = logging.getLogger(__name__)

app.config.from_object(__name__)
mail = Mail(application)


def get_conf(section, key, default=None):
    try:
        value = config.get(section, key)
    except (NoSectionError, NoOptionError) as e:
        log.error("Error getting config... (exception: %s)" % e)
        return default
    return value

DEBUG = get_conf('main', 'debug', False)
MAIL_SERVER = get_conf('email', 'server', 'smtp.gmail.com')
MAIL_PORT = get_conf('email', 'port', 465)
MAIL_USE_TLS = get_conf('email', 'tls', False)
MAIL_USE_SSL = get_conf('email', 'ssl', True)
CSRF_ENABLED = get_conf('main', 'csrf', False)  # TODO: Add CSRF Protection :)
REDIS_HOST = get_conf('redis', 'host', 'localhost')
REDIS_PORT = get_conf('redis', 'port', 6379)
REDIS_DB = get_conf('redis', 'db', 0)  # TODO: get_int?


# Skills
LANGUAGES = [
    {'language': 'Python', 'perc': 100},
    {'language': 'Javascript', 'perc': 60},
    {'language': 'Java', 'perc': 30},
    {'language': 'Bash', 'perc': 30},
    {'language': 'CSS', 'perc': 30},
    {'language': 'HTML', 'perc': 30},
    {'language': 'Mako', 'perc': 30},
    {'language': 'Jinja2', 'perc': 30},
    {'language': 'SQLite', 'perc': 30},
    {'language': 'MySQL', 'perc': 30},
    {'language': 'C', 'perc': 20},
    {'language': 'C++', 'perc': 5},
    {'language': 'PHP', 'perc': 5},
    {'language': 'MASM', 'perc': 1}
]

TECHNOLOGIES = [
    {'technology': 'Git', 'perc': 100},
    {'technology': 'Mercurial', 'perc': 100},
    {'technology': 'Pylons', 'perc': 100},
    {'technology': 'Flask', 'perc': 100},
    {'technology': 'Docker', 'perc': 100},
    {'technology': 'Ubuntu', 'perc': 100},
    {'technology': 'OSX', 'perc': 100},
    {'technology': 'Wordpress', 'perc': 100},
    {'technology': 'Vagrant', 'perc': 100},
    {'technology': 'RabbitMQ', 'perc': 100},
    {'technology': 'Apache', 'perc': 100},
    {'technology': 'Django', 'perc': 100},
    {'technology': 'Subversion', 'perc': 100},
    {'technology': 'JQuery', 'perc': 100},
    {'technology': 'Drupal', 'perc': 100},
    {'technology': 'Flot', 'perc': 100},
    {'technology': 'SQL Migration', 'perc': 100},
    {'technology': 'Buildbot', 'perc': 100},
    {'technology': 'Redis', 'perc': 100},
    {'technology': 'Nagios', 'perc': 100},
    {'technology': 'Node.js', 'perc': 100},
    {'technology': 'Grunt', 'perc': 100},
    {'technology': 'Travis', 'perc': 100},
    {'technology': 'Memcached', 'perc': 100}
]


def send_email(form):
    msg = Message(
        subject='CONTACT ME: ' + form.name.data,
        sender=form.email.data,
        recipients=['johnlzeller@gmail.com']
    )
    msg.body = form.message.data
    try:
        mail.send(msg)
    except Exception as e:
        print e
        form.success = False
        return form
    form.success = True

    return form


def get_json(conn, key):
    data = conn.get(key)
    return json.loads(data)


@app.route('/', methods=['GET', 'POST'])
def home():
    log.info("Opening redis connection...")
    pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    conn = redis.Redis(connection_pool=pool)

    form = ContactForm()
    if form.validate_on_submit():
        form = send_email(form)

    return render_template(
        'index.html',
        form=form,
        language_experience=LANGUAGES,
        technology_experience=TECHNOLOGIES,
        fitness=get_json(conn, 'runkeeper_data'),
        commit=get_json(conn, 'github_data'),
        current_temp=get_json(conn, 'temp_f'),
        nutrition_info=get_json(conn, 'myfitnesspal_data'),
        blog_posts=[]
    )

if __name__ == '__main__':
    log.info("Starting web app...")
    app.run()
