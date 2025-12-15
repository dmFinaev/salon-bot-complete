"""
REPOSITORY INTERFACE: Определяем контракт для работы с клиентами
В Clean Architecture интерфейсы в домене, реализация в инфраструктуре
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.client import Client


class IClientRepository(ABC):
    """Интерфейс репозитория клиентов"""
    
    @abstractmethod
    def save(self, client: Client) -> Client:
        """Сохранить клиента"""
        pass
    
    @abstractmethod
    def find_by_id(self, client_id: int) -> Optional[Client]:
        """Найти клиента по ID"""
        pass
    
    @abstractmethod
    def find_by_telegram_id(self, telegram_id: str) -> Optional[Client]:
        """Найти клиента по Telegram ID"""
        pass
    
    @abstractmethod
    def find_by_phone(self, phone: str) -> Optional[Client]:
        """Найти клиента по телефону"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Client]:
        """Получить всех клиентов"""
        pass
    
    @abstractmethod
    def delete(self, client_id: int) -> bool:
        """Удалить клиента"""
        pass
    
    @abstractmethod
    def update(self, client: Client) -> Client:
        """Обновить клиента"""
        pass
