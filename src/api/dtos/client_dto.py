"""
DTO (Data Transfer Object): Клиент
Используется для передачи данных между слоями
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class ClientDTO:
    """DTO для передачи данных о клиенте"""
    
    id: Optional[int] = None
    name: str = ""
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    created_at: Optional[datetime] = None
    notes: str = ""
    
    @property
    def has_telegram(self) -> bool:
        """Есть ли Telegram у клиента?"""
        return bool(self.telegram_id)
    
    @property
    def formatted_phone(self) -> str:
        """Форматированный телефон"""
        if not self.phone:
            return "Не указан"
        
        # Простое форматирование
        phone = ''.join(filter(str.isdigit, self.phone))
        if len(phone) == 11:
            return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:]}"
        return self.phone
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'telegram_id': self.telegram_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClientDTO':
        """Создание из словаря"""
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            phone=data.get('phone'),
            telegram_id=data.get('telegram_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            notes=data.get('notes', '')
        )
