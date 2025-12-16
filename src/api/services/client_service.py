"""
Service Layer: Сервис для работы с клиентами
Связывает Use Cases с Telegram
"""

from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from src.core.application.use_cases.create_client_use_case import CreateClientUseCase
from src.core.domain.entities.client import Client
from src.core.domain.exceptions.client_exceptions import (
    InvalidClientDataException,
    DuplicateClientException
)
from src.api.dtos.client_dto import ClientDTO


class ClientService:
    """Сервис для операций с клиентами"""
    
    def __init__(self, client_repository):
        self.client_repo = client_repository
        self.create_use_case = CreateClientUseCase(client_repository)
    
    async def register_client(
        self, 
        name: str, 
        phone: str, 
        telegram_id: str
    ) -> Tuple[ClientDTO, bool, Optional[str]]:
        """
        Регистрация клиента
        
        Returns:
            Tuple[client_dto, is_new, error_message]
        """
        try:
            # Используем Use Case
            client_entity, is_new = self.create_use_case.execute(
                name=name,
                phone=phone,
                telegram_id=telegram_id
            )
            
            # Конвертируем Entity в DTO
            client_dto = self._entity_to_dto(client_entity)
            
            return client_dto, is_new, None
            
        except InvalidClientDataException as e:
            return None, False, f"Ошибка данных: {str(e)}"
            
        except DuplicateClientException as e:
            return None, False, f"Клиент уже существует: {str(e)}"
            
        except Exception as e:
            return None, False, f"Неизвестная ошибка: {str(e)}"
    
    async def get_client_by_telegram(self, telegram_id: str) -> Optional[ClientDTO]:
        """Получение клиента по Telegram ID"""
        client_entity = self.client_repo.find_by_telegram_id(telegram_id)
        
        if not client_entity:
            return None
        
        return self._entity_to_dto(client_entity)
    
    async def update_client_phone(
        self, 
        telegram_id: str, 
        new_phone: str
    ) -> Tuple[Optional[ClientDTO], Optional[str]]:
        """Обновление телефона клиента"""
        client_entity = self.client_repo.find_by_telegram_id(telegram_id)
        
        if not client_entity:
            return None, "Клиент не найден"
        
        try:
            from src.core.domain.entities.client import PhoneNumber
            client_entity.phone = PhoneNumber(new_phone)
            
            updated_entity = self.client_repo.update(client_entity)
            client_dto = self._entity_to_dto(updated_entity)
            
            return client_dto, None
            
        except ValueError as e:
            return None, f"Неверный формат телефона: {str(e)}"
    
    async def get_client_stats(self, telegram_id: str) -> Dict[str, Any]:
        """Статистика клиента"""
        client_entity = self.client_repo.find_by_telegram_id(telegram_id)
        
        if not client_entity:
            return {"error": "Клиент не найден"}
        
        # Здесь позже добавим статистику по записям
        stats = {
            "client_id": client_entity.id,
            "name": client_entity.name,
            "phone": str(client_entity.phone) if client_entity.phone else "Не указан",
            "has_telegram": client_entity.has_telegram(),
            "registration_date": client_entity.created_at.strftime("%d.%m.%Y") if client_entity.created_at else "Неизвестно",
            "total_bookings": 0,  # TODO: добавить когда будет репозиторий записей
            "upcoming_bookings": 0,
            "completed_bookings": 0,
        }
        
        return stats
    
    def _entity_to_dto(self, client_entity: Client) -> ClientDTO:
        """Конвертация Entity в DTO"""
        return ClientDTO(
            id=client_entity.id,
            name=client_entity.name,
            phone=str(client_entity.phone) if client_entity.phone else None,
            telegram_id=client_entity.telegram_id,
            created_at=client_entity.created_at,
            notes=client_entity.notes
        )
    
    def _dto_to_entity(self, client_dto: ClientDTO) -> Client:
        """Конвертация DTO в Entity"""
        from src.core.domain.entities.client import Client, PhoneNumber
        
        phone_obj = None
        if client_dto.phone:
            phone_obj = PhoneNumber(client_dto.phone)
        
        return Client(
            id=client_dto.id,
            name=client_dto.name,
            phone=phone_obj,
            telegram_id=client_dto.telegram_id,
            created_at=client_dto.created_at or datetime.now(),
            notes=client_dto.notes
        )
