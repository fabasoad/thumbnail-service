import asyncio
import errno
import json
import logging
import os
import threading
import uuid

from .redis_factory import RedisFactory
from .thumbnail_processor import ThumbnailProcessor

class ThumbnailException(Exception):

    def __init__(self, reason):
        self.reason = reason

class FileValidationException(ThumbnailException):

    def __init__(self, reason):
        ThumbnailException.__init__(self, reason)   

class ThumbnailService:

    FORM_PARAMETER = 'image'
    THUMBNAIL_PATH = os.environ.get('THUMBNAIL_PATH', '/usr/images/')

    def __init__(self, redis_factory=RedisFactory()):
        self.log = logging.getLogger('ThumbnailService')
        self.redis_factory = redis_factory
        self.processor = ThumbnailProcessor()
    
    def get_file(self, id):
        return self._build_file_entity(self._get_file_info(id))
    
    def get_files(self):
        redis = self.redis_factory.create_instance()
        data = redis.mget(redis.keys('file-*'))
        return [self._build_file_entity(json.loads(info)) for info in data]

    async def save_file(self, reader):
        field = await reader.next()
        while field is not None and field.name != self.FORM_PARAMETER:
            field = await reader.next()

        if field is None:
            raise FileValidationException('\"{}\" parameter is missing'.format(self.FORM_PARAMETER))

        redis = self.redis_factory.create_instance()
        
        id = str(uuid.uuid4())
        self._try_create_folder()
        size = await self._try_save_file(field, id)
        info = {
            'id': id,
            'filename': field.filename,
            'path': self.THUMBNAIL_PATH,
            'ready': False,
            'size': {
                'original': size
            }
        }
        redis.set(self._build_key(info['id']), json.dumps(info))
        self._run_save_file(info)
        return self._build_file_entity(info)

    def _run_save_file(self, info):
        def _run():
            file_path = os.path.join(self.THUMBNAIL_PATH, info['id'])
            self.processor.process(file_path)
            info['size']['thumbnail'] = os.stat(self.processor.build_thumbnail_filename(file_path)).st_size
            info['ready'] = True
            redis = self.redis_factory.create_instance()
            redis.set(self._build_key(info['id']), json.dumps(info))

        threading.Thread(target=_run).start()

    def _try_create_folder(self):
        if not os.path.exists(self.THUMBNAIL_PATH):
            try:
                os.makedirs(self.THUMBNAIL_PATH)
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise ThumbnailException('Failed to access to the image storage')
    
    async def _try_save_file(self, field, filename):
        size = 0
        with open(os.path.join(self.THUMBNAIL_PATH, filename), 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                f.write(chunk)
        return size

    def delete_file(self, id):
        redis = self.redis_factory.create_instance()
        info = self._get_file_info(id, redis)
        file_path = os.path.join(info['path'], info['id'])
        os.remove(file_path)
        os.remove(self.processor.build_thumbnail_filename(file_path))
        redis.delete(self._build_key(id))
        return self._build_file_entity(info)
    
    def get_thumbnail_info(self, id):
        info = self._get_file_info(id)
        path = os.path.join(info['path'], self.processor.build_thumbnail_filename(info['id']))
        splitted = os.path.splitext(info['filename'])
        return {
            'path': path,
            'filename': self.processor.build_thumbnail_filename(splitted[0]) + '.jpg'
        }

    def _get_file_info(self, id, redis=None):        
        redis = redis or self.redis_factory.create_instance()
        key = self._build_key(id)
        data = redis.get(key)
        if data is None:
            raise FileValidationException('Thumbnail with id = {} does not exist'.format(id))
        return json.loads(data)
    
    def _build_key(self, filename):
        return 'file-{}'.format(filename)
    
    def _build_file_entity(self, data):
        result = {
            'id': data['id'],
            'filename': data['filename'],
            'ready': data['ready'],
            'size': {
                'original': data['size']['original']
            }
        }
        if data['ready']:
            result['size']['thumbnail'] = data['size']['thumbnail']
        return result