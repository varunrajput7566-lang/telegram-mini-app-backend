import logging
import hmac
import hashlib
from aiohttp import web
from config import settings

logger = logging.getLogger(__name__)

async def verify_telegram_user(request: web.Request) -> bool:
    """Verify telegram user from request"""
    try:
        # Get Telegram init data from header
        init_data = request.headers.get('X-Telegram-Init-Data')
        
        if not init_data:
            return False
        
        # Parse query string
        params = dict(pair.split('=') for pair in init_data.split('&'))
        hash_param = params.pop('hash')
        
        # Create signature
        data_check_string = '\n'.join(
            f'{k}={v}' for k, v in sorted(params.items())
        )
        
        secret_key = hmac.new(
            b'WebAppData',
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_hash, hash_param)
    
    except Exception as e:
        logger.error(f"Error verifying telegram user: {e}")
        return False
