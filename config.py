from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Ads Platforms
    ADSGRAM_API_KEY: str
    ADSGRAM_CLIENT_ID: str
    ADSGRAM_SECRET: str
    
    ONCLICKA_API_KEY: str
    ONCLICKA_CLIENT_ID: str
    ONCLICKA_SECRET: str
    
    # Server
    BACKEND_URL: str
    FRONTEND_URL: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Settings
    ADS_PER_PLATFORM: int = 15
    TASKS_PER_DAY: int = 10
    REWARD_AMOUNT: float = 10.0
    MIN_WITHDRAWAL: float = 300.0
    AD_DURATION: int = 30  # seconds
    TASK_DURATION: int = 30  # seconds
    
    # Garbage Collection
    GC_INTERVAL: int = 86400  # 24 hours
    DB_CLEANUP_INTERVAL: int = 604800  # 7 days
    DB_RETENTION_DAYS: int = 3
    
    # Broadcast
    BROADCAST_DELAY: int = 5  # seconds
    BROADCAST_USER_THRESHOLD: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
