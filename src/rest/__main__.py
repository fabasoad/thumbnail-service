import os
import sys

from aiohttp import web
from .middlewares import error_middleware
from .system_resources import SystemResource
from .thumbnail_resources import ThumbnailResource

DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080

host = os.environ.get('THUMBNAIL_BACKEND_HOST', DEFAULT_HOST)
port = os.environ.get('THUMBNAIL_BACKEND_PORT', DEFAULT_PORT)

system_resources = SystemResource(web)
thumbnail_resource = ThumbnailResource(web)

app = web.Application(middlewares=[error_middleware])
app.add_routes(system_resources.routes + thumbnail_resource.routes)
web.run_app(app, host=host, port=port)
