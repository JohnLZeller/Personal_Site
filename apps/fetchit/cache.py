# stdlib
from config import get_base_config

import json
import logging
import redis

log = logging.getLogger(__name__)
config = get_base_config()


class RedisCache(object):
    HOST = config.get('redis', 'host') or 'localhost'
    PORT = config.getint('redis', 'port') or 6379
    DB = config.getint('redis', 'db') or 0

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def __init__(self):
        pool = redis.ConnectionPool(host=self.HOST, port=self.PORT, db=self.DB)
        self.conn = redis.Redis(
            connection_pool=pool,
            password=config.get('redis', 'password')
        )

    def get_json(self, key):
        data = self.conn.get(key)
        return json.loads(data)

    def set_json(self, key, data):
        data = json.dumps(data)
        return self.conn.set(key, data)
