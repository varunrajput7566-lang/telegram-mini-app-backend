import logging
from aiohttp import web
from app.services.supabase_service import supabase_service
from app.middleware.auth import verify_telegram_user
from config import settings
from datetime import date

logger = logging.getLogger(__name__)

async def complete_task(request: web.Request) -> web.Response:
    """Record that user completed a task"""
    try:
        data = await request.json()
        telegram_id = data.get('telegram_id')
        task_id = data.get('task_id')
        task_type = data.get('task_type')  # 'join_channel', 'join_group', 'start_bot'
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        # Get user
        user = await supabase_service.get_user(telegram_id)
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        # Check daily limit (10 tasks per day)
        today = date.today().isoformat()
        last_reward_date = user.get('last_reward_date')
        
        tasks_completed_today = user.get('tasks_completed_today', 0)
        
        if last_reward_date != today:
            tasks_completed_today = 0
        
        if tasks_completed_today >= 10:
            return web.json_response({
                'success': False,
                'message': 'Daily task limit reached (10 tasks)'
            }, status=400)
        
        # Update user
        new_tasks_count = tasks_completed_today + 1
        updates = {
            'tasks_completed_today': new_tasks_count,
            'tasks_completed_total': user.get('tasks_completed_total', 0) + 1,
        }
        
        # Check if reward should be given (30 ads + 10 tasks)
        ads_watched_today = user.get('ads_watched_today', 0)
        
        if new_tasks_count == 10 and ads_watched_today >= 30:
            # Give reward
            updates['balance'] = user.get('balance', 0) + settings.REWARD_AMOUNT
            updates['last_reward_date'] = today
        
        await supabase_service.update_user(telegram_id, updates)
        
        return web.json_response({
            'success': True,
            'message': 'Task recorded successfully',
            'tasks_completed': new_tasks_count,
            'reward_given': updates.get('last_reward_date') == today
        })
    
    except Exception as e:
        logger.error(f"Error in complete_task: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_task_stats(request: web.Request) -> web.Response:
    """Get user's task statistics"""
    try:
        telegram_id = int(request.match_info.get('telegram_id'))
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        user = await supabase_service.get_user(telegram_id)
        
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        today = date.today().isoformat()
        last_reward_date = user.get('last_reward_date')
        
        if last_reward_date != today:
            tasks_completed_today = 0
        else:
            tasks_completed_today = user.get('tasks_completed_today', 0)
        
        return web.json_response({
            'tasks_completed_total': tasks_completed_today,
            'tasks_limit': 10,
        })
    
    except Exception as e:
        logger.error(f"Error in get_task_stats: {e}")
        return web.json_response({'error': str(e)}, status=500)
