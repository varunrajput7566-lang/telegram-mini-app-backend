from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    telegram_id: int
    name: str
    username: str
    balance: float = 0.0
    ads_watched_today: int = 0
    tasks_completed_today: int = 0
    ads_watched_total: int = 0
    tasks_completed_total: int = 0
    total_withdrawn: float = 0.0
    upi_id: Optional[str] = None
    phone: Optional[str] = None
    last_reward_date: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'name': self.name,
            'username': self.username,
            'balance': self.balance,
            'ads_watched_today': self.ads_watched_today,
            'tasks_completed_today': self.tasks_completed_today,
            'ads_watched_total': self.ads_watched_total,
            'tasks_completed_total': self.tasks_completed_total,
            'total_withdrawn': self.total_withdrawn,
            'upi_id': self.upi_id,
            'phone': self.phone,
            'last_reward_date': self.last_reward_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
