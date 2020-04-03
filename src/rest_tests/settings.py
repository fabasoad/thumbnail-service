import os

settings = {
    'schema': os.environ.get('REST_SCHEMA', 'http'),
    'host': os.environ.get('REST_HOST', '127.0.0.1'),
    'port': os.environ.get('REST_PORT', 8080)
}

base_url = '{}://{}:{}'.format(settings['schema'], settings['host'], settings['port'])