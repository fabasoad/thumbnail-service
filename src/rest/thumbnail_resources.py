import logging
import os

from aiohttp import web
from ..service.thumbnail_service import ThumbnailService

class ThumbnailResource:

    def __init__(self, web):
        self.log = logging.getLogger('ThumbnailResource')
        self.service = ThumbnailService()
        self.routes = [
            web.get('/api/v1/thumbnail', self.get_files),
            web.get('/api/v1/thumbnail/{id}', self.get_file),
            web.get('/api/v1/thumbnail/{id}/download', self.download_file),
            web.post('/api/v1/thumbnail', self.upload_file),
            web.delete('/api/v1/thumbnail/{id}', self.delete_file)
        ]

    async def get_files(self, request):
        result = self.service.get_files()
        return web.json_response(result)

    async def get_file(self, request):
        id = request.match_info['id']
        result = self.service.get_file(id)
        return web.json_response(result)

    async def upload_file(self, request):
        result = await self.service.save_file(await request.multipart())
        return web.json_response(result, status=201)
    
    async def delete_file(self, request):
        id = request.match_info['id']
        result = self.service.delete_file(id)
        return web.json_response(result)
    
    async def download_file(self, request):
        id = request.match_info['id']
        info = self.service.get_thumbnail_info(id)
        return web.FileResponse(info['path'], headers={
            'Content-Disposition': 'attachment;filename=' + info['filename']
        })
