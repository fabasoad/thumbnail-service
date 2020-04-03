import aiohttp
import json
import pytest

import settings

@pytest.mark.asyncio
async def test_pulse():
    async with aiohttp.ClientSession() as session:
        async with session.get('{}/api/v1/system/pulse'.format(settings.base_url)) as resp:
            assert resp.status == 200
            res = json.loads(await resp.text())
            assert res['alive'] == True