import hashlib
import json
import os
import pytest
import sys
import uuid

from ..thumbnail_service import ThumbnailService, FileValidationException
from ..redis_factory import RedisFactory

from redis import Redis
from unittest.mock import mock_open, patch, MagicMock

# TODO: save_file and get_file

def test_get_files():
    expected = {
        "id": str(uuid.uuid4()),
        "filename": 'abc123',
        "size": 123
    }
    keys_result = 'def321'
    with patch.object(Redis, 'keys', return_value=keys_result) as mock_keys:
        with patch.object(Redis, 'mget', return_value=[json.dumps(expected)]) as mock_mget:
            redis = Redis()
            redis_factory = RedisFactory()
            redis_factory.create_instance = MagicMock(return_value = redis)
            service = ThumbnailService(redis_factory)
            assert service.get_files() == [expected]
            mock_mget.assert_called_once_with(keys_result)
            mock_keys.assert_called_once_with(_build_key('*'))

@patch('os.path.exists')
@patch('os.makedirs')
@patch("builtins.open", new_callable=mock_open, read_data="data")
@pytest.mark.asyncio
async def test_save_file_with_empty_reader_result(mock_os_path_exists, mock_os_makedirs, mock_open):
    await _save_file_with_invalid_reader(mock_os_path_exists, mock_os_makedirs, mock_open, lambda: ReaderMock(0))

@patch('os.path.exists')
@patch('os.makedirs')
@patch("builtins.open", new_callable=mock_open, read_data="data")
@pytest.mark.asyncio
async def test_save_file_with_invalid_reader_result(mock_os_path_exists, mock_os_makedirs, mock_open):
    await _save_file_with_invalid_reader(mock_os_path_exists, mock_os_makedirs, mock_open, lambda: ReaderMock(3))

async def _save_file_with_invalid_reader(mock_os_path_exists, mock_os_makedirs, mock_open, reader_factory):
    with patch.object(Redis, 'set') as mock_set:
        redis = Redis()
        redis_factory = RedisFactory()
        redis_factory.create_instance = MagicMock(return_value = redis)
        service = ThumbnailService(redis_factory)
        try:
            await service.save_file(reader_factory())
            assert False
        except FileValidationException:
            mock_set.assert_not_called()
            mock_os_path_exists.assert_not_called()
            mock_os_makedirs.assert_not_called()
            mock_open.assert_not_called()

def _mock_uuid():
    return uuid.UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')

@patch('os.remove')
def test_delete_file_positive(mock_os_remove):
    test_id = "1234-5678-90"
    get_result = {
        'path': "/test/",
        'filename': "abcdef",
        'id': test_id,
        'size': {
            'original': 456,
            'thumbnail': 456
        }
    }
    with patch.object(Redis, 'get', return_value=json.dumps(get_result)) as mock_get:
        with patch.object(Redis, 'delete') as mock_delete:
            expected_key = _build_key(test_id)
            redis = Redis()
            redis_factory = RedisFactory()
            redis_factory.create_instance = MagicMock(return_value = redis)
            service = ThumbnailService(redis_factory)
            assert service.delete_file(test_id) == {
                'id': get_result['id'],
                'filename': get_result['filename'],
                'size': get_result['size']
            }
            mock_get.assert_called_once_with(expected_key)
            mock_delete.assert_called_once_with(expected_key)
            mock_os_remove.assert_called_once_with(
                os.path.join(get_result['path'], get_result['id']))

@patch('os.remove')
def test_delete_file_negative(mock_os_remove):
    test_id = "1234-5678-90"
    with patch.object(Redis, 'get', return_value=None) as mock_get:
        with patch.object(Redis, 'delete') as mock_delete:
            expected_key = _build_key(test_id)
            redis = Redis()
            redis_factory = RedisFactory()
            redis_factory.create_instance = MagicMock(return_value = redis)
            service = ThumbnailService(redis_factory)
            try:
                service.delete_file(test_id)
            except FileValidationException:                
                mock_get.assert_called_once_with(expected_key)
                mock_delete.assert_not_called()
                mock_os_remove.assert_not_called()
                return
            assert False

def _build_key(filename):
    return 'file-{}'.format(filename)

class ReaderMock:
    def __init__(self, limit, name='abc123', filename=None):
        self.counter = 0
        self.limit = limit
        self.name = name
        self.filename = filename

    async def next(self):
        if self.counter == self.limit:
            return None
        else:
            self.counter += 1
            return ReaderFieldMock(self.name, self.filename)

class ReaderFieldMock:
    def __init__(self, name, filename):
        self.name = name
        self.filename = filename

    async def read_chunk(self):
        return False