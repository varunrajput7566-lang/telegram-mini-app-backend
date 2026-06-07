import asyncio
from supabase import create_client, Client
from config import settings
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    
    # User operations
    async def create_user(self, telegram_id: int, name: str, username: str) -> Dict[str, Any]:
        """Create a new user in the database"""
        try:
            response = self.client.table('users').insert({
                'telegram_id': telegram_id,
                'name': name,
                'username': username,
                'balance': 0.0,
                'ads_watched_today': 0,
                'tasks_completed_today': 0,
                'ads_watched_total': 0,
                'tasks_completed_total': 0,
                'total_withdrawn': 0.0,
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Get user by telegram ID"""
        try:
            response = self.client.table('users').select('*').eq('telegram_id', telegram_id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    async def update_user(self, telegram_id: int, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            response = self.client.table('users').update(updates).eq('telegram_id', telegram_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    async def add_balance(self, telegram_id: int, amount: float) -> bool:
        """Add balance to user"""
        try:
            user = await self.get_user(telegram_id)
            if not user:
                return False
            
            new_balance = user.get('balance', 0) + amount
            return await self.update_user(telegram_id, {'balance': new_balance})
        except Exception as e:
            logger.error(f"Error adding balance: {e}")
            return False
    
    async def deduct_balance(self, telegram_id: int, amount: float) -> bool:
        """Deduct balance from user"""
        try:
            user = await self.get_user(telegram_id)
            if not user or user.get('balance', 0) < amount:
                return False
            
            new_balance = user.get('balance', 0) - amount
            return await self.update_user(telegram_id, {'balance': new_balance})
        except Exception as e:
            logger.error(f"Error deducting balance: {e}")
            return False
    
    async def get_leaderboard(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard sorted by balance"""
        try:
            response = self.client.table('users').select('telegram_id, username, balance').order('balance', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def create_withdrawal_request(self, telegram_id: int, amount: float, upi_id: str, phone: str) -> Dict[str, Any]:
        """Create withdrawal request"""
        try:
            response = self.client.table('withdrawal_requests').insert({
                'telegram_id': telegram_id,
                'amount': amount,
                'upi_id': upi_id,
                'phone': phone,
                'status': 'pending',
            }).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating withdrawal request: {e}")
            return None
    
    async def get_withdrawal_requests(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get withdrawal requests for user"""
        try:
            response = self.client.table('withdrawal_requests').select('*').eq('telegram_id', telegram_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting withdrawal requests: {e}")
            return []
    
    async def update_withdrawal_status(self, request_id: int, status: str) -> bool:
        """Update withdrawal request status"""
        try:
            response = self.client.table('withdrawal_requests').update({'status': status}).eq('id', request_id).execute()
            return bool(response.data)
        except Exception as e:
            logger.error(f"Error updating withdrawal status: {e}")
            return False
    
    # Cleanup operations
    async def delete_old_ads(self, days: int = 3) -> int:
        """Delete ads older than specified days"""
        try:
            response = self.client.table('ad_views').delete().lt('created_at', f'now()-interval \'{days} days\'').execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Error deleting old ads: {e}")
            return 0
    
    async def delete_old_task_completions(self, days: int = 3) -> int:
        """Delete task completions older than specified days"""
        try:
            response = self.client.table('task_completions').delete().lt('created_at', f'now()-interval \'{days} days\'').execute()
            return len(response.data) if response.data else 0
        except Exception as e:
            logger.error(f"Error deleting old task completions: {e}")
            return 0

# Singleton instance
supabase_service = SupabaseService()
