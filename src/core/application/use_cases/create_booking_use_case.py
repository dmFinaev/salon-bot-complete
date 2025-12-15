"""
USE CASE: Создание новой записи
Use Case - бизнес-сценарий, координирует работу Entity и Repository
"""

from typing import Tuple, Optional
from datetime import date, time
from uuid import uuid4

from ...domain.entities.booking import Booking
from ...domain.entities.client import Client
from ...domain.value_objects.service_type import ServiceType
from ...domain.repositories.booking_repository import IBookingRepository
from ...domain.repositories.client_repository import IClientRepository
from ...domain.exceptions.booking_exceptions import (
    BookingTimeConflictException,
    ServiceUnavailableException,
    MasterUnavailableException
)


class CreateBookingUseCase:
    """
    Use Case: Создание новой записи
    
    Use Case должен:
    1. Принимать входные данные (DTO)
    2. Выполнять бизнес-логику
    3. Координировать работу Entity и Repository
    4. Возвращать результат или выбрасывать исключение
    """
    
    def __init__(
        self,
        booking_repository: IBookingRepository,
        client_repository: IClientRepository
    ):
        self.booking_repo = booking_repository
        self.client_repo = client_repository
    
    def execute(
        self,
        client_id: int,
        service: ServiceType,
        booking_date: date,
        start_time: time,
        master_id: Optional[int] = None,
        notes: str = ""
    ) -> Tuple[Booking, bool]:
        """
        Основной метод Use Case
        
        Args:
            client_id: ID клиента
            service: Услуга (Value Object)
            booking_date: Дата записи
            start_time: Время начала
            master_id: ID мастера (опционально)
            notes: Дополнительные заметки
        
        Returns:
            Tuple[созданная_запись, была_ли_проведена_валидация_конфликтов]
        
        Raises:
            BookingTimeConflictException: Если время уже занято
            ServiceUnavailableException: Если услуга недоступна
            MasterUnavailableException: Если мастер недоступен
        """
        
        # 1. Проверяем клиента
        client = self.client_repo.find_by_id(client_id)
        if not client:
            raise ValueError(f"Клиент с ID {client_id} не найден")
        
        # 2. Создаем Entity Booking
        new_booking = Booking(
            client_id=client_id,
            master_id=master_id,
            service=service,
            booking_date=booking_date,
            start_time=start_time,
            notes=notes
        )
        
        # 3. Проверяем конфликты времени
        has_conflicts = self._check_time_conflicts(new_booking)
        
        if has_conflicts:
            # Бизнес-правило: нельзя создавать конфликтующие записи
            raise BookingTimeConflictException(
                "Выбранное время уже занято. Пожалуйста, выберите другое время."
            )
        
        # 4. Проверяем доступность услуги (дополнительная бизнес-логика)
        if not self._is_service_available(service, booking_date):
            raise ServiceUnavailableException(
                f"Услуга '{service.name}' недоступна на выбранную дату"
            )
        
        # 5. Проверяем доступность мастера
        if master_id and not self._is_master_available(master_id, booking_date):
            raise MasterUnavailableException(
                f"Мастер с ID {master_id} недоступен на выбранную дату"
            )
        
        # 6. Сохраняем в репозиторий
        saved_booking = self.booking_repo.save(new_booking)
        
        # 7. Логируем создание (для аудита)
        self._log_booking_creation(saved_booking, client)
        
        return saved_booking, has_conflicts
    
    def _check_time_conflicts(self, booking: Booking) -> bool:
        """Проверка конфликтов времени"""
        # Вычисляем end_time если еще не вычислено
        if booking.end_time is None:
            booking._calculate_end_time()
        
        # Ищем конфликтующие записи
        conflicting = self.booking_repo.find_conflicting_bookings(
            master_id=booking.master_id,
            booking_date=booking.booking_date,
            start_time=booking.start_time,
            end_time=booking.end_time or booking.start_time,
            exclude_booking_id=booking.id
        )
        
        return len(conflicting) > 0
    
    def _is_service_available(
        self, 
        service: ServiceType, 
        target_date: date
    ) -> bool:
        """Проверка доступности услуги"""
        # Здесь может быть сложная бизнес-логика:
        # - Проверка графика работы салона
        # - Проверка праздничных дней
        # - Проверка загрузки мастеров и т.д.
        
        # Пока реализуем простую проверку:
        # Услуга доступна все дни кроме воскресенья
        if target_date.weekday() == 6:  # Воскресенье
            return False
        
        # Проверяем время работы салона (10:00 - 20:00)
        # Это упрощенная версия
        return True
    
    def _is_master_available(
        self, 
        master_id: int, 
        target_date: date
    ) -> bool:
        """Проверка доступности мастера"""
        # Получаем записи мастера на эту дату
        master_bookings = self.booking_repo.find_by_master(master_id)
        
        # Фильтруем по дате и активным статусам
        bookings_on_date = [
            b for b in master_bookings 
            if b.booking_date == target_date and b.is_active
        ]
        
        # Простая проверка: если у мастера больше 8 записей - он занят
        return len(bookings_on_date) < 8
    
    def _log_booking_creation(self, booking: Booking, client: Client):
        """Логирование создания записи (для аудита)"""
        # В реальном приложении здесь могла бы быть
        # интеграция с системой логирования
        print(
            f"[AUDIT] Создана запись: "
            f"ID={booking.id}, "
            f"Клиент={client.name}, "
            f"Дата={booking.formatted_datetime}, "
            f"Услуга={booking.service.name}"
        )
