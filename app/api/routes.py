from aiohttp import web
from app.api import users, withdrawal, leaderboard, ads, tasks

def setup_routes(app: web.Application):
    """Setup all API routes"""
    
    # User routes
    app.router.add_post('/api/users/create', users.create_user)
    app.router.add_get('/api/users/{telegram_id}', users.get_user)
    app.router.add_get('/api/users/{telegram_id}/balance', users.get_user_balance)
    
    # Ad routes
    app.router.add_post('/api/ads/watched', ads.record_ad_watched)
    app.router.add_get('/api/ads/stats/{telegram_id}', ads.get_ad_stats)
    
    # Task routes
    app.router.add_post('/api/tasks/complete', tasks.complete_task)
    app.router.add_get('/api/tasks/stats/{telegram_id}', tasks.get_task_stats)
    
    # Withdrawal routes
    app.router.add_post('/api/withdrawal/request', withdrawal.create_withdrawal_request)
    app.router.add_get('/api/withdrawal/history/{telegram_id}', withdrawal.get_withdrawal_history)
    
    # Leaderboard routes
    app.router.add_get('/api/leaderboard', leaderboard.get_leaderboard)
    
    # Health check
    async def health_check(request):
        return web.json_response({'status': 'ok'})
    
    app.router.add_get('/health', health_check)
