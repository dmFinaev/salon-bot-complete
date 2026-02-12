"""
USE CASE: Создание клиента
В Clean Architecture use cases содержат бизнес-правила приложения
"""

from typing import Tuple
from ...domain.entities.client import Client
from ...domain.repositories.client_repository import IClientRepository
from ...domain.exceptions.client_exceptions import (
    InvalidClientDataException, 
    DuplicateClientException
)


class CreateClientUseCase:
    """Use Case: Создание нового клиента"""
    
    def __init__(self, client_repository: IClientRepository):
        self.client_repo = client_repository
    
    def execute(self, name: str, phone: str, telegram_id: str = None) -> Tuple[Client, bool]:
        """
        Основной метод use case
        Возвращает: (клиент, был_ли_создан_новый)
        """
        # 1. Валидация входных данных
        if not name or len(name.strip()) < 2:
            raise InvalidClientDataException("Имя должно быть минимум 2 символа")
        
        # 2. Проверяем, нет ли уже клиента с таким телефоном
        existing_by_phone = self.client_repo.find_by_phone(phone)
        if existing_by_phone:
            # Если нашли по телефону, проверяем Telegram ID
            if telegram_id and existing_by_phone.telegram_id != telegram_id:
                # Обновляем Telegram ID если он новый
                existing_by_phone.telegram_id = telegram_id
                updated_client = self.client_repo.update(existing_by_phone)
                return updated_client, False
            return existing_by_phone, False
        
        # 3. Проверяем по Telegram ID
        if telegram_id:
            existing_by_tg = self.client_repo.find_by_telegram_id(telegram_id)
            if existing_by_tg:
                # Если Telegram есть, но телефон другой - обновляем телефон
                from ...domain.entities.client import PhoneNumber
                existing_by_tg.phone = PhoneNumber(phone)
                updated_client = self.client_repo.update(existing_by_tg)
                return updated_client, False
        
        # 4. Создаем нового клиента
        from ...domain.entities.client import Client, PhoneNumber
        phone_obj = PhoneNumber(phone)
        
        new_client = Client(
            name=name.strip(),
            phone=phone_obj,
            telegram_id=telegram_id
        )
        
        # 5. Сохраняем в репозиторий
        saved_client = self.client_repo.save(new_client)
        
        return saved_client, True
