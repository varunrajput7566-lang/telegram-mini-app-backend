from aiohttp import web
from app.api import users, withdrawal, leaderboard
from app.webhooks import adsgram, onclicka

def setup_routes(app: web.Application):
    """Setup all API routes"""
    
    # User routes
    app.router.add_post('/api/users/create', users.create_user)
    app.router.add_get('/api/users/{telegram_id}', users.get_user)
    app.router.add_get('/api/users/{telegram_id}/balance', users.get_user_balance)
    
    # Withdrawal routes
    app.router.add_post('/api/withdrawal/request', withdrawal.create_withdrawal_request)
    app.router.add_get('/api/withdrawal/history/{telegram_id}', withdrawal.get_withdrawal_history)
    
    # Leaderboard routes
    app.router.add_get('/api/leaderboard', leaderboard.get_leaderboard)
    
    # Adsgram webhook routes
    app.router.add_post('/webhooks/adsgram/ad-watched', adsgram.adsgram_ad_watched)
    app.router.add_post('/webhooks/adsgram/task-completed', adsgram.adsgram_task_completed)
    app.router.add_get('/api/adsgram/ads', adsgram.adsgram_get_ads)
    app.router.add_get('/api/adsgram/tasks', adsgram.adsgram_get_tasks)
    
    # Onclicka webhook routes
    app.router.add_post('/webhooks/onclicka/ad-watched', onclicka.onclicka_ad_watched)
    app.router.add_get('/api/onclicka/ads', onclicka.onclicka_get_ads)
    
    # Health check
    async def health_check(request):
        return web.json_response({'status': 'ok'})
    
    app.router.add_get('/health', health_check)
