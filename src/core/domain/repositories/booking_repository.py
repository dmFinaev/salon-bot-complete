"""
REPOSITORY INTERFACE: Контракт для работы с записями
Интерфейс в домене, реализация в инфраструктуре
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, datetime
from ...domain.entities.booking import Booking
from ...domain.value_objects.booking_status import BookingStatus


class IBookingRepository(ABC):
    """Интерфейс репозитория записей"""
    
    @abstractmethod
    def save(self, booking: Booking) -> Booking:
        """Сохранить запись"""
        pass
    
    @abstractmethod
    def find_by_id(self, booking_id: int) -> Optional[Booking]:
        """Найти запись по ID"""
        pass
    
    @abstractmethod
    def find_by_uuid(self, uuid: str) -> Optional[Booking]:
        """Найти запись по UUID"""
        pass
    
    @abstractmethod
    def find_by_client(self, client_id: int) -> List[Booking]:
        """Найти все записи клиента"""
        pass
    
    @abstractmethod
    def find_by_master(self, master_id: int) -> List[Booking]:
        """Найти все записи мастера"""
        pass
    
    @abstractmethod
    def find_by_date(self, target_date: date) -> List[Booking]:
        """Найти записи на конкретную дату"""
        pass
    
    @abstractmethod
    def find_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Booking]:
        """Найти записи в диапазоне дат"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        """Найти записи по статусу"""
        pass
    
    @abstractmethod
    def find_conflicting_bookings(
        self,
        master_id: Optional[int],
        booking_date: date,
        start_time: datetime.time,
        end_time: datetime.time,
        exclude_booking_id: Optional[int] = None
    ) -> List[Booking]:
        """
        Найти конфликтующие записи
        
        Args:
            master_id: ID мастера (если None - проверяем всех)
            booking_date: Дата записи
            start_time: Время начала
            end_time: Время окончания
            exclude_booking_id: ID записи для исключения (при обновлении)
        
        Returns:
            Список конфликтующих записей
        """
        pass
    
    @abstractmethod
    def update(self, booking: Booking) -> Booking:
        """Обновить запись"""
        pass
    
    @abstractmethod
    def delete(self, booking_id: int) -> bool:
        """Удалить запись"""
        pass
    
    @abstractmethod
    def count_by_client(self, client_id: int) -> int:
        """Количество записей клиента"""
        pass
    
    @abstractmethod
    def get_upcoming_bookings(self, days_ahead: int = 7) -> List[Booking]:
        """Получить предстоящие записи"""
        pass
