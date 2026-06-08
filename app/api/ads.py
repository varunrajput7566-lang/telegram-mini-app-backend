import logging
from aiohttp import web
from app.services.supabase_service import supabase_service
from app.middleware.auth import verify_telegram_user
from config import settings
from datetime import date

logger = logging.getLogger(__name__)

async def record_ad_watched(request: web.Request) -> web.Response:
    """Record that user watched an ad"""
    try:
        data = await request.json()
        telegram_id = data.get('telegram_id')
        platform = data.get('platform')  # 'adsgram' or 'onclicka'
        watched_duration = data.get('watched_duration', 0)
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        # Only count if watched for 30 seconds
        if watched_duration < 30:
            return web.json_response({
                'success': False,
                'message': f'Ad must be watched for 30 seconds (watched: {watched_duration}s)'
            }, status=400)
        
        # Get user
        user = await supabase_service.get_user(telegram_id)
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        # Check daily limit (30 total ads)
        today = date.today().isoformat()
        last_reward_date = user.get('last_reward_date')
        
        ads_watched_today = user.get('ads_watched_today', 0)
        
        if last_reward_date != today:
            # Reset counters for new day
            ads_watched_today = 0
        
        if ads_watched_today >= 30:
            return web.json_response({
                'success': False,
                'message': 'Daily ad limit reached (30 ads)'
            }, status=400)
        
        # Check platform limit (15 per platform)
        if platform == 'adsgram':
            adsgram_limit_key = 'adsgram_ads_today'
            adsgram_count = user.get(adsgram_limit_key, 0)
            if adsgram_count >= 15:
                return web.json_response({
                    'success': False,
                    'message': 'Adsgram daily limit reached (15 ads)'
                }, status=400)
        elif platform == 'onclicka':
            onclicka_limit_key = 'onclicka_ads_today'
            onclicka_count = user.get(onclicka_limit_key, 0)
            if onclicka_count >= 15:
                return web.json_response({
                    'success': False,
                    'message': 'Onclicka daily limit reached (15 ads)'
                }, status=400)
        
        # Update user
        new_ads_count = ads_watched_today + 1
        updates = {
            'ads_watched_today': new_ads_count,
            'ads_watched_total': user.get('ads_watched_total', 0) + 1,
        }
        
        # Update platform-specific count
        if platform == 'adsgram':
            updates['adsgram_ads_today'] = user.get('adsgram_ads_today', 0) + 1
        elif platform == 'onclicka':
            updates['onclicka_ads_today'] = user.get('onclicka_ads_today', 0) + 1
        
        # Check if reward should be given (30 ads + 10 tasks)
        if new_ads_count == 30:
            tasks_completed_today = user.get('tasks_completed_today', 0)
            
            if tasks_completed_today >= 10:
                # Give reward
                updates['balance'] = user.get('balance', 0) + settings.REWARD_AMOUNT
                updates['last_reward_date'] = today
        
        await supabase_service.update_user(telegram_id, updates)
        
        return web.json_response({
            'success': True,
            'message': 'Ad recorded successfully',
            'ads_watched': new_ads_count,
            'reward_given': updates.get('last_reward_date') == today
        })
    
    except Exception as e:
        logger.error(f"Error in record_ad_watched: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_ad_stats(request: web.Request) -> web.Response:
    """Get user's ad watching statistics"""
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
            # Reset counts for new day
            ads_watched_today = 0
            adsgram_count = 0
            onclicka_count = 0
        else:
            ads_watched_today = user.get('ads_watched_today', 0)
            adsgram_count = user.get('adsgram_ads_today', 0)
            onclicka_count = user.get('onclicka_ads_today', 0)
        
        return web.json_response({
            'ads_watched_total': ads_watched_today,
            'ads_watched_limit': 30,
            'adsgram_ads': adsgram_count,
            'adsgram_limit': 15,
            'onclicka_ads': onclicka_count,
            'onclicka_limit': 15,
        })
    
    except Exception as e:
        logger.error(f"Error in get_ad_stats: {e}")
        return web.json_response({'error': str(e)}, status=500)
