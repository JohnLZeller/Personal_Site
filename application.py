#!/usr/bin/env python
from config import get_base_config, initialize_logging  # noqa

from flask import Flask, render_template

from flask_mail import Mail, Message

from forms import ContactForm

import json
import logging
import redis

initialize_logging()
log = logging.getLogger(__name__)

# App setup
application = Flask(__name__)
app = application
app.config.from_object('config')

# Globals
mail = Mail(app)
config = get_base_config()

REDIS_HOST = config.get('redis', 'host') or 'localhost'
REDIS_PORT = config.getint('redis', 'port') or 6379
REDIS_DB = config.getint('redis', 'db') or 0


def send_email(form):
    sender_name = form.name.data
    sender_email = form.email.data
    log.info("Sending an email from %s, %s" % (sender_name, sender_email))
    msg = Message(
        subject='CONTACT ME: %s' % sender_name,
        sender=sender_email,
        recipients=['johnlzeller@gmail.com'],
        body=form.message.data
    )
    try:
        mail.send(msg)
    except Exception as e:
        log.error("Email sending failed! (exception: %s" % str(e))
        form.success = False
        # TODO: Show an error, don't just redirect
        return form
    log.info("Email sent successfully!")
    form.success = True

    return form


def get_json(conn, key):
    data = conn.get(key)
    return json.loads(data)


@app.route('/', methods=['GET', 'POST'])
def home():
    log.info("Opening redis connection...")
    section = None
    pool = redis.ConnectionPool(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=config.get('redis', 'password')
    )
    conn = redis.StrictRedis(connection_pool=pool)

    form = ContactForm()
    if form.validate_on_submit():
        form = send_email(form)
        section = 'contact'

    references = [{
        'image': 'https://media.licdn.com/mpr/mpr/shrinknp_100_100/AAEAAQAAAAAAAAFBAAAAJGE1ZjU0MDg4LTY5OGQtNGFiOS05ZGYzLTcwZjc4NzFkMTEzMA.jpg',
        'name': 'Ricky Thomas',
        'title': 'Solutions Engineer at Datadog',
        'text': (
            "Working with John for almost two years was a great experience. As a Solutions Engineer I'd escalate certain cases to "
            "him I wasn't able to resolve. He would always give clear explanations and provide resolutions quickly! He's a fun, "
            "friendly, genuine individual who know's what he's talking about and can quickly resolve issues effectively. John and "
            "I did a hack day project together where he had built an entirely brand new dynamic UI for our project overnight. We "
            "even won a prize! John is a great guy who loves what he does and is great at it! I'd recommend him to any company."
        )},
        {
        'image': 'https://media.licdn.com/mpr/mpr/shrinknp_100_100/p/8/000/1ed/0fc/325cbcf.jpg',
        'name': 'David Merrick',
        'title': 'Software Quality Engineer at Jive Software',
        'text': (
            "When I met John, he was enrolled in a full credit load in the engineering program at Oregon State University, leading "
            "the Mars Rover team for the Robotics Club, and singlehandedly spearheading Advocates for Space Exploration, the "
            "nonprofit he founded that later gained international media attention and drove over 31,000 petition signatures on "
            "Change.org. He is one of the most ambitious people I know, yet is also one of the most trustworthy, creative, and "
            "friendly. He is an excellent leader, and the enthusiasm he brings to everything he does is inspiring."
        )},
    ]

    return render_template(
        'index.html',
        section=section,
        form=form,
        fitness=get_json(conn, 'runkeeper_data'),
        commit=get_json(conn, 'github_data'),
        current_temp=get_json(conn, 'temp_f'),
        nutrition_info=get_json(conn, 'myfitnesspal_data'),
        references=references
    )

if __name__ == '__main__':
    log.info("Starting web app...")
    app.run()
