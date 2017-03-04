#!/usr/bin/env python
from config import get_base_config, initialize_logging  # noqa

from flask import Flask, render_template
from flask.ext.mail import Mail, Message

from forms import ContactForm

import json
import logging
import redis

initialize_logging()

# App setup
application = Flask(__name__)
app = application
app.config.from_object('config')

# Globals
mail = Mail(application)
log = logging.getLogger(__name__)
config = get_base_config()

MAIL_SERVER = config.get('email', 'server') or 'smtp.gmail.com'
MAIL_PORT = config.getint('email', 'port') or 465
MAIL_USERNAME = config.get('email', 'username') or ''
MAIL_PASSWORD = config.get('email', 'password') or ''
MAIL_USE_TLS = config.getboolean('email', 'tls') or False
MAIL_USE_SSL = config.getboolean('email', 'ssl') or True
CSRF_ENABLED = config.getboolean('main', 'csrf') or False  # TODO: CSRF :)
REDIS_HOST = config.get('redis', 'host') or 'localhost'
REDIS_PORT = config.getint('redis', 'port') or 6379
REDIS_DB = config.getint('redis', 'db') or 0


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
        fitness=get_json(conn, 'runkeeper_data'),
        commit=get_json(conn, 'github_data'),
        current_temp=get_json(conn, 'temp_f'),
        nutrition_info=get_json(conn, 'myfitnesspal_data'),
        blog_posts=[]
    )

if __name__ == '__main__':
    log.info("Starting web app...")
    app.run()
