import logging
from datetime import datetime, timedelta
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

class DatabaseCleaner:
    async def cleanup_old_data(self, retention_days: int = 3) -> Dict[str, int]:
        """Clean up old data from database"""
        try:
            results = {
                'old_ads_deleted': await supabase_service.delete_old_ads(retention_days),
                'old_tasks_deleted': await supabase_service.delete_old_task_completions(retention_days),
            }
            
            logger.info(f"🧹 Database cleanup results: {results}")
            return results
        except Exception as e:
            logger.error(f"Error in database cleanup: {e}")
            return {}

db_cleaner = DatabaseCleaner()
