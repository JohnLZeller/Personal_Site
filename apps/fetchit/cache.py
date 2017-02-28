# stdlib
import json
import logging
import redis

# project
from utils import get_conf

# TODO: Does this actually work with just string and not logging.INFO?
# TODO: Move to utils or something
logging.basicConfig(
    filename=get_conf('main', 'log_file', 'fetchit.log'),
    level=get_conf('main', 'log_level', logging.INFO)
)
log = logging.getLogger(__name__)


class RedisCache(object):
    HOST = get_conf('redis', 'host', 'localhost')
    PORT = get_conf('redis', 'port', 6379)
    DB = get_conf('redis', 'db', 0)  # TODO: get_int?

    # TODO: Check all responses for {u'message': u'Bad credentials'}

    def __init__(self):
        pool = redis.ConnectionPool(host=self.HOST, port=self.PORT, db=self.DB)
        self.conn = redis.Redis(connection_pool=pool)

    def get_json(self, key):
        data = self.conn.get(key)
        return json.loads(data)

    def set_json(self, key, data):
        data = json.dumps(data)
        return self.conn.set(key, data)
