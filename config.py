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
