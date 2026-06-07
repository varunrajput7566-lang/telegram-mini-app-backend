import hmac
import hashlib
import logging
from config import settings

logger = logging.getLogger(__name__)

class WebhookVerifier:
    @staticmethod
    def verify_adsgram_signature(data: str, signature: str) -> bool:
        """Verify Adsgram webhook signature"""
        try:
            expected_signature = hmac.new(
                settings.ADSGRAM_SECRET.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying Adsgram signature: {e}")
            return False
    
    @staticmethod
    def verify_onclicka_signature(data: str, signature: str) -> bool:
        """Verify Onclicka webhook signature"""
        try:
            expected_signature = hmac.new(
                settings.ONCLICKA_SECRET.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error verifying Onclicka signature: {e}")
            return False

webhook_verifier = WebhookVerifier()
