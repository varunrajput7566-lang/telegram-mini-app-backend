from aiohttp import web
from app.services.supabase_service import supabase_service
from app.middleware.auth import verify_telegram_user
import json
import logging

logger = logging.getLogger(__name__)

async def create_user(request: web.Request) -> web.Response:
    """Create or update user profile"""
    try:
        data = await request.json()
        telegram_id = data.get('telegram_id')
        name = data.get('name')
        username = data.get('username')
        
        # Validate telegram user
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        # Check if user exists
        existing_user = await supabase_service.get_user(telegram_id)
        
        if existing_user:
            # Update existing user
            updated = await supabase_service.update_user(telegram_id, {
                'name': name,
                'username': username,
            })
            return web.json_response({
                'success': updated,
                'user': existing_user if not updated else await supabase_service.get_user(telegram_id)
            })
        else:
            # Create new user
            user = await supabase_service.create_user(telegram_id, name, username)
            return web.json_response({'success': bool(user), 'user': user})
    
    except Exception as e:
        logger.error(f"Error in create_user: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_user(request: web.Request) -> web.Response:
    """Get user profile"""
    try:
        telegram_id = int(request.match_info.get('telegram_id'))
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        user = await supabase_service.get_user(telegram_id)
        
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        return web.json_response(user)
    
    except Exception as e:
        logger.error(f"Error in get_user: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_user_balance(request: web.Request) -> web.Response:
    """Get user balance"""
    try:
        telegram_id = int(request.match_info.get('telegram_id'))
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        user = await supabase_service.get_user(telegram_id)
        
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        return web.json_response({
            'balance': user.get('balance', 0),
            'ads_watched_today': user.get('ads_watched_today', 0),
            'tasks_completed_today': user.get('tasks_completed_today', 0),
        })
    
    except Exception as e:
        logger.error(f"Error in get_user_balance: {e}")
        return web.json_response({'error': str(e)}, status=500)
