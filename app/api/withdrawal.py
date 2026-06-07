import logging
import asyncio
from aiohttp import web
from app.services.supabase_service import supabase_service
from app.middleware.auth import verify_telegram_user
from config import settings
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

# Track withdrawal requests per user for rate limiting
withdrawal_queue = defaultdict(list)

async def create_withdrawal_request(request: web.Request) -> web.Response:
    """Create a withdrawal request"""
    try:
        data = await request.json()
        telegram_id = data.get('telegram_id')
        amount = float(data.get('amount', 0))
        upi_id = data.get('upi_id')
        phone = data.get('phone')
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        # Validate minimum withdrawal
        if amount < settings.MIN_WITHDRAWAL:
            return web.json_response({
                'error': f'Minimum withdrawal is {settings.MIN_WITHDRAWAL} rupees'
            }, status=400)
        
        # Get user
        user = await supabase_service.get_user(telegram_id)
        if not user:
            return web.json_response({'error': 'User not found'}, status=404)
        
        # Check balance
        if user.get('balance', 0) < amount:
            return web.json_response({'error': 'Insufficient balance'}, status=400)
        
        # Add to queue with delay
        queue_position = len(withdrawal_queue[telegram_id])
        delay = queue_position * 1  # 1 second delay per request
        
        # Create withdrawal request
        withdrawal = await supabase_service.create_withdrawal_request(
            telegram_id, amount, upi_id, phone
        )
        
        if not withdrawal:
            return web.json_response({'error': 'Failed to create request'}, status=500)
        
        # Deduct balance
        await supabase_service.deduct_balance(telegram_id, amount)
        
        # Add to queue for processing
        withdrawal_queue[telegram_id].append({
            'id': withdrawal.get('id'),
            'delay': delay,
            'created_at': datetime.now().isoformat()
        })
        
        return web.json_response({
            'success': True,
            'withdrawal_id': withdrawal.get('id'),
            'status': 'pending',
            'message': 'Your withdrawal request is in review',
            'delay_seconds': delay,
        })
    
    except Exception as e:
        logger.error(f"Error in create_withdrawal_request: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def get_withdrawal_history(request: web.Request) -> web.Response:
    """Get user withdrawal history"""
    try:
        telegram_id = int(request.match_info.get('telegram_id'))
        
        if not await verify_telegram_user(request):
            return web.json_response({'error': 'Unauthorized'}, status=401)
        
        withdrawals = await supabase_service.get_withdrawal_requests(telegram_id)
        
        return web.json_response({
            'withdrawals': withdrawals,
            'count': len(withdrawals)
        })
    
    except Exception as e:
        logger.error(f"Error in get_withdrawal_history: {e}")
        return web.json_response({'error': str(e)}, status=500)
