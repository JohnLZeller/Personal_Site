from ConfigParser import SafeConfigParser

import logging
import logging.config
import logging.handlers

import os
import sys
import traceback

MAX_LOG_BYTES = 10 * 1024 * 1024
CFG_FILENAME = 'config.ini'
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
LOG_FORMAT = (
    '%(asctime)s | %(levelname)s | '
    '%(name)s(%(filename)s:%(lineno)s) | %(message)s'
)
DEBUG = False
SECRET_KEY = ''
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_USE_TLS = False
MAIL_USE_SSL = True
CSRF_ENABLED = True
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

log = logging.getLogger(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))


def get_base_config():
    config_path = '%s/%s' % (basedir, CFG_FILENAME)
    config = SafeConfigParser()
    config.read(config_path)
    return config


def get_logging_config():
    config = get_base_config()

    levels = {
        'CRITICAL': logging.CRITICAL,
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'FATAL': logging.FATAL,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'WARNING': logging.WARNING,
    }

    return {
        'log_filepath': config.get('main', 'log_filepath'),
        'log_format': config.get('main', 'log_format'),
        'log_level': levels.get(config.get('main', 'log_level'))
    }


def initialize_logging():
    try:
        logging_config = get_logging_config()

        logging.basicConfig(
            format=LOG_FORMAT,
            level=logging_config.get('log_level') or logging.INFO
        )

        log_filepath = logging_config.get('log_filepath')
        if log_filepath:
            dir_name = os.path.dirname(log_filepath)
            if os.access(dir_name, os.R_OK | os.W_OK):
                handler = logging.handlers.RotatingFileHandler(
                    log_filepath,
                    maxBytes=MAX_LOG_BYTES,
                    backupCount=1
                )
                handler.setFormatter(
                    logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
                )
                base_log = logging.getLogger()
                base_log.addHandler(handler)
            else:
                sys.stderr.write("Directory '%s' not writable!\n" % dir_name)
    except Exception as e:
        sys.stderr.write("Log init failed! (exception: %s)\n" % str(e))
        traceback.print_exc()
        logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    # Set log global
    global log
    log = logging.getLogger(__name__)

# Load config constants
base_conf = get_base_config()
SECRET_KEY = base_conf.get('main', 'secret_key') or ''
MAIL_SERVER = base_conf.get('email', 'server') or 'smtp.gmail.com'
MAIL_PORT = base_conf.getint('email', 'port') or 465
MAIL_USERNAME = base_conf.get('email', 'username') or ''
MAIL_PASSWORD = base_conf.get('email', 'password') or ''
MAIL_USE_TLS = base_conf.getboolean('email', 'tls') or False
MAIL_USE_SSL = base_conf.getboolean('email', 'ssl') or True
CSRF_ENABLED = base_conf.getboolean('main', 'csrf') or True
REDIS_HOST = base_conf.get('redis', 'host') or 'localhost'
REDIS_PORT = base_conf.getint('redis', 'port') or 6379
REDIS_DB = base_conf.getint('redis', 'db') or 0
