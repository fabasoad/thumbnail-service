import aiohttp
import os
import pytest
import time

import settings

from aiohttp import FormData

async def call_get(url, handler):
    async with aiohttp.ClientSession() as session:
        async with session.get(settings.base_url + url) as resp:
            assert resp.status == 200
            await handler(await resp.json())

async def call_delete(url, handler):
    async with aiohttp.ClientSession() as session:
        async with session.delete(settings.base_url + url) as resp:
            assert resp.status == 200
            await handler(await resp.json())

async def call_upload_file(url, filename, handler):
    filepath = os.path.join(os.getcwd(), 'src', 'rest_tests', filename)
    async with aiohttp.ClientSession() as session:
        data = FormData()
        data.add_field(
            'image',
            open(filepath, 'rb'),
            filename=filename
        )
        async with session.post(settings.base_url + url, data=data) as resp:
            assert resp.status == 201
            await handler(await resp.json())

@pytest.mark.asyncio    
async def test_full_lifecycle():
    async def get_all_handler1(res1):
        assert res1 == []
        expected_file_name = 'test.jpg'

        async def upload_handler(res2):
            assert 'id' in res2
            assert len(res2['id']) > 0

            async def get_handler(res3, timeout):
                assert 'id' in res3
                assert len(res3['id']) > 0
                assert res3['filename'] == expected_file_name
                assert res3['size']['original'] > 0

                async def delete_handler(res4):
                    assert res4 == res3

                    async def get_all_handler2(res5):
                        assert res5 == []

                    await call_get('/api/v1/thumbnail', get_all_handler2)

                if res3['size']['thumbnail'] > 0:
                    await call_delete('/api/v1/thumbnail/' + res3['id'], delete_handler)
                elif timeout > 0:
                    time.sleep(3)
                    await call_get('/api/v1/thumbnail/' + res2['id'], lambda r: get_handler(r, timeout - 1))
                else:
                    raise Exception('Timeout error')

            await call_get('/api/v1/thumbnail/' + res2['id'], lambda r: get_handler(r, 3))

        await call_upload_file('/api/v1/thumbnail', expected_file_name, upload_handler)

    await call_get('/api/v1/thumbnail', get_all_handler1)