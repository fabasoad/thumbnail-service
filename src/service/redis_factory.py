import os
import redis

class RedisFactory:

    DEFAULT_HOST = '0.0.0.0'
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0

    def __init__(self):        
        self.host = os.environ.get('REDIS_HOST', self.DEFAULT_HOST)
        self.port = os.environ.get('REDIS_PORT', self.DEFAULT_PORT)
        self.db = os.environ.get('REDIS_DB', self.DEFAULT_DB)
        self.password = os.environ['REDIS_PASSWORD']

    def create_instance(self, **kwargs):
        return redis.Redis(
            host=self.host,
            port=self.port,
            password=self.password,
            db=self.db,
            decode_responses=True,
            **kwargs
        )