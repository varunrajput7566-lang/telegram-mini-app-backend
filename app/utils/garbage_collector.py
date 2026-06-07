import gc
import psutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GarbageCollector:
    def __init__(self):
        self.process = psutil.Process()
        self.collection_count = 0
    
    def collect(self) -> Dict[str, Any]:
        """Run garbage collection and return statistics"""
        try:
            # Get memory before
            mem_before = self.process.memory_info().rss / 1024 / 1024  # MB
            
            # Run garbage collection
            collected = gc.collect()
            
            # Get memory after
            mem_after = self.process.memory_info().rss / 1024 / 1024  # MB
            
            self.collection_count += 1
            
            stats = {
                'timestamp': datetime.now().isoformat(),
                'collected_objects': collected,
                'memory_before_mb': round(mem_before, 2),
                'memory_after_mb': round(mem_after, 2),
                'memory_freed_mb': round(mem_before - mem_after, 2),
                'collection_count': self.collection_count,
            }
            
            logger.info(f"🗑️  GC Stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Error in garbage collection: {e}")
            return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            return {
                'memory_mb': round(self.process.memory_info().rss / 1024 / 1024, 2),
                'cpu_percent': self.process.cpu_percent(interval=1),
                'num_threads': self.process.num_threads(),
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return None

gc_manager = GarbageCollector()
