import logging
from aiohttp import web
from app.services.supabase_service import supabase_service
from app.middleware.auth import verify_telegram_user

logger = logging.getLogger(__name__)

async def get_leaderboard(request: web.Request) -> web.Response:
    """Get leaderboard"""
    try:
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        limit = int(request.rel_url.query.get('limit', 100))
        
        leaderboard = await supabase_service.get_leaderboard(limit)
        
        # Add rank
        for idx, user in enumerate(leaderboard, 1):
            user['rank'] = idx
        
        return web.json_response({
            'leaderboard': leaderboard,
            'updated_at': 'Daily at 12:01 AM',
        })
    
    except Exception as e:
        logger.error(f"Error in get_leaderboard: {e}")
        return web.json_response({'error': str(e)}, status=500)
