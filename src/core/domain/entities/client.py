"""
ENTITY: Клиент (бизнес-сущность)
В Clean Architecture entities содержат бизнес-правила
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.phone import PhoneNumber
from ..exceptions.client_exceptions import InvalidClientDataException


@dataclass
class Client:
    """Сущность клиента салона красоты"""
    
    id: Optional[int] = None
    name: str = ""
    phone: Optional[PhoneNumber] = None
    telegram_id: Optional[str] = None
    created_at: datetime = None
    notes: str = ""
    
    def __post_init__(self):
        """Валидация при создании объекта"""
        if not self.name or len(self.name.strip()) < 2:
            raise InvalidClientDataException("Имя клиента должно быть минимум 2 символа")
        
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def update_name(self, new_name: str):
        """Бизнес-правило: обновление имени"""
        if not new_name or len(new_name.strip()) < 2:
            raise InvalidClientDataException("Новое имя слишком короткое")
        self.name = new_name.strip()
    
    def has_telegram(self) -> bool:
        """Проверка, есть ли у клиента Telegram"""
        return bool(self.telegram_id and self.telegram_id.strip())
    
    def can_receive_notifications(self) -> bool:
        """Может ли клиент получать уведомления"""
        return self.has_telegram() and self.phone is not None
    
    def __str__(self) -> str:
        return f"Client(id={self.id}, name='{self.name}', phone={self.phone})"


# Value Object для номера телефона
@dataclass(frozen=True)  # frozen делает объект неизменяемым
class PhoneNumber:
    """Value Object: номер телефона"""
    number: str
    
    def __post_init__(self):
        if not self._is_valid_phone(self.number):
            raise ValueError(f"Неверный формат телефона: {self.number}")
    
    @staticmethod
    def _is_valid_phone(phone: str) -> bool:
        """Простая валидация российских номеров"""
        import re
        pattern = r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
        return bool(re.match(pattern, phone))
    
    def formatted(self) -> str:
        """Форматированный номер"""
        clean = ''.join(filter(str.isdigit, self.number))
        if clean.startswith('8'):
            clean = '7' + clean[1:]
        return f"+7 ({clean[1:4]}) {clean[4:7]}-{clean[7:9]}-{clean[9:]}"
    
    def __repr__(self):
        return self.formatted()
