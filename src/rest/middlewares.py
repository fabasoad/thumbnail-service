from aiohttp import web

from ..service.thumbnail_service import ThumbnailException, FileValidationException

@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except FileValidationException as ex:
        return web.json_response({ 'error': ex.reason }, status=400)
    except ThumbnailException as ex:
        return web.json_response({ 'error': ex.reason }, status=500)
    except web.HTTPException as ex:
        return web.json_response({ 'error': ex.reason }, status=ex.status_code)
    except Exception as ex:
        return web.json_response({ 'error': str(ex) }, status=500)