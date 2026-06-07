from aiohttp import web
from config import settings

def setup_cors(app: web.Application):
    """Setup CORS middleware"""
    
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == 'OPTIONS':
                return web.Response(
                    status=200,
                    headers={
                        'Access-Control-Allow-Origin': settings.FRONTEND_URL,
                        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Signature',
                        'Access-Control-Max-Age': '3600',
                    }
                )
            
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = settings.FRONTEND_URL
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Signature'
            
            return response
        
        return middleware_handler
    
    app.middlewares.append(cors_middleware)
