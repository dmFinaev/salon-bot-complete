"""
In-Memory Repository: Клиенты
Временная реализация для тестирования
"""

from typing import List, Optional, Dict
from src.core.domain.entities.client import Client
from src.core.domain.repositories.client_repository import IClientRepository


class InMemoryClientRepository(IClientRepository):
    """In-memory реализация репозитория клиентов"""
    
    def __init__(self):
        self._clients: Dict[int, Client] = {}
        self._telegram_index: Dict[str, Client] = {}
        self._phone_index: Dict[str, Client] = {}
        self._next_id = 1
    
    def save(self, client: Client) -> Client:
        """Сохранить клиента"""
        if client.id is None:
            client.id = self._next_id
            self._next_id += 1
        
        self._clients[client.id] = client
        
        # Обновляем индексы
        if client.telegram_id:
            self._telegram_index[client.telegram_id] = client
        
        if client.phone:
            self._phone_index[str(client.phone)] = client
        
        return client
    
    def find_by_id(self, client_id: int) -> Optional[Client]:
        """Найти клиента по ID"""
        return self._clients.get(client_id)
    
    def find_by_telegram_id(self, telegram_id: str) -> Optional[Client]:
        """Найти клиента по Telegram ID"""
        return self._telegram_index.get(telegram_id)
    
    def find_by_phone(self, phone: str) -> Optional[Client]:
        """Найти клиента по телефону"""
        # Ищем точное совпадение
        client = self._phone_index.get(phone)
        if client:
            return client
        
        # Ищем нормализованный номер
        from src.core.domain.entities.client import PhoneNumber
        try:
            phone_obj = PhoneNumber(phone)
            return self._phone_index.get(str(phone_obj))
        except:
            return None
    
    def find_all(self) -> List[Client]:
        """Получить всех клиентов"""
        return list(self._clients.values())
    
    def delete(self, client_id: int) -> bool:
        """Удалить клиента"""
        if client_id not in self._clients:
            return False
        
        client = self._clients[client_id]
        
        # Удаляем из индексов
        if client.telegram_id and client.telegram_id in self._telegram_index:
            del self._telegram_index[client.telegram_id]
        
        if client.phone and str(client.phone) in self._phone_index:
            del self._phone_index[str(client.phone)]
        
        # Удаляем из основного хранилища
        del self._clients[client_id]
        
        return True
    
    def update(self, client: Client) -> Client:
        """Обновить клиента"""
        if client.id not in self._clients:
            raise ValueError(f"Клиент с ID {client.id} не найден")
        
        old_client = self._clients[client.id]
        
        # Обновляем индексы если изменились данные
        if old_client.telegram_id != client.telegram_id:
            if old_client.telegram_id:
                del self._telegram_index[old_client.telegram_id]
            if client.telegram_id:
                self._telegram_index[client.telegram_id] = client
        
        if old_client.phone != client.phone:
            if old_client.phone:
                del self._phone_index[str(old_client.phone)]
            if client.phone:
                self._phone_index[str(client.phone)] = client
        
        # Сохраняем клиента
        self._clients[client.id] = client
        
        return client
