import json
import logging
from aiohttp import web
from app.webhooks.verification import webhook_verifier
from app.services.supabase_service import supabase_service
from config import settings
from datetime import datetime, date

logger = logging.getLogger(__name__)

async def adsgram_ad_watched(request: web.Request) -> web.Response:
    """Handle Adsgram ad watched webhook"""
    try:
        # Verify signature
        signature = request.headers.get('X-Signature')
        body = await request.text()
        
        if not webhook_verifier.verify_adsgram_signature(body, signature):
            return web.json_response({'error': 'Invalid signature'}, status=401)
        
        data = json.loads(body)
        telegram_id = data.get('user_id')
        ad_id = data.get('ad_id')
        watch_duration = data.get('watch_duration', 0)
        
        # Only count if watched for 30 seconds
        if watch_duration < settings.AD_DURATION:
            return web.json_response({
                'success': False,
                'message': 'Ad not watched for 30 seconds'
            })
        
        # Get user
        user = await supabase_service.get_user(telegram_id)
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        # Check daily limit (15 from Adsgram)
        today = date.today().isoformat()
        last_reward_date = user.get('last_reward_date')
        
        ads_watched_today = user.get('ads_watched_today', 0)
        
        if last_reward_date != today:
            # Reset counters for new day
            ads_watched_today = 0
        
        if ads_watched_today >= 30:  # Total limit
            return web.json_response({
                'success': False,
                'message': 'Daily ad limit reached'
            })
        
        # Update user
        new_ads_count = ads_watched_today + 1
        updates = {
            'ads_watched_today': new_ads_count,
            'ads_watched_total': user.get('ads_watched_total', 0) + 1,
        }
        
        # Check if reward should be given
        if new_ads_count == 30:
            # Check if all tasks completed
            tasks_completed_today = user.get('tasks_completed_today', 0)
            
            if tasks_completed_today >= 10:
                # Give reward
                updates['balance'] = user.get('balance', 0) + settings.REWARD_AMOUNT
                updates['last_reward_date'] = today
        
        await supabase_service.update_user(telegram_id, updates)
        
        return web.json_response({
            'success': True,
            'message': 'Ad watched successfully',
            'ads_watched': new_ads_count,
        })
    
    except Exception as e:
        logger.error(f"Error in adsgram_ad_watched: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def adsgram_task_completed(request: web.Request) -> web.Response:
    """Handle Adsgram task completed webhook"""
    try:
        # Verify signature
        signature = request.headers.get('X-Signature')
        body = await request.text()
        
        if not webhook_verifier.verify_adsgram_signature(body, signature):
            return web.json_response({'error': 'Invalid signature'}, status=401)
        
        data = json.loads(body)
        telegram_id = data.get('user_id')
        task_id = data.get('task_id')
        
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
                'message': 'Daily task limit reached'
            })
        
        # Update user
        new_tasks_count = tasks_completed_today + 1
        updates = {
            'tasks_completed_today': new_tasks_count,
            'tasks_completed_total': user.get('tasks_completed_total', 0) + 1,
        }
        
        # Check if reward should be given
        ads_watched_today = user.get('ads_watched_today', 0)
        
        if new_tasks_count == 10 and ads_watched_today >= 30:
            # Give reward
            updates['balance'] = user.get('balance', 0) + settings.REWARD_AMOUNT
            updates['last_reward_date'] = today
        
        await supabase_service.update_user(telegram_id, updates)
        
        return web.json_response({
            'success': True,
            'message': 'Task completed successfully',
            'tasks_completed': new_tasks_count,
        })
    
    except Exception as e:
        logger.error(f"Error in adsgram_task_completed: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def adsgram_get_ads(request: web.Request) -> web.Response:
    """Get ads from Adsgram"""
    try:
        # Verify request
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        telegram_id = int(request.rel_url.query.get('telegram_id'))
        
        # Call Adsgram API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://adsgram-api.com/v1/ads',
                headers={'Authorization': f'Bearer {settings.ADSGRAM_API_KEY}'},
                params={'client_id': settings.ADSGRAM_CLIENT_ID, 'user_id': telegram_id}
            ) as resp:
                ads = await resp.json()
                return web.json_response(ads)
    
    except Exception as e:
        logger.error(f"Error in adsgram_get_ads: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def adsgram_get_tasks(request: web.Request) -> web.Response:
    """Get tasks from Adsgram"""
    try:
        # Verify request
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        telegram_id = int(request.rel_url.query.get('telegram_id'))
        
        # Call Adsgram API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://adsgram-api.com/v1/tasks',
                headers={'Authorization': f'Bearer {settings.ADSGRAM_API_KEY}'},
                params={'client_id': settings.ADSGRAM_CLIENT_ID, 'user_id': telegram_id}
            ) as resp:
                data = await resp.json()
                
                # Auto-complete bypass: if no tasks available
                if not data.get('tasks') or len(data.get('tasks', [])) == 0:
                    user = await supabase_service.get_user(telegram_id)
                    if user and user.get('ads_watched_today', 0) >= 30:
                        # All ads watched, complete automatically
                        await supabase_service.update_user(telegram_id, {
                            'tasks_completed_today': 10,
                        })
                        return web.json_response({
                            'auto_completed': True,
                            'message': 'No tasks available, but all ads watched'
                        })
                
                return web.json_response(data)
    
    except Exception as e:
        logger.error(f"Error in adsgram_get_tasks: {e}")
        return web.json_response({'error': str(e)}, status=500)
