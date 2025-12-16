"""
In-Memory Repository: Записи
Временная реализация для тестирования
"""

from typing import List, Optional, Dict
from datetime import date, datetime
from src.core.domain.entities.booking import Booking
from src.core.domain.repositories.booking_repository import IBookingRepository
from src.core.domain.value_objects.booking_status import BookingStatus


class InMemoryBookingRepository(IBookingRepository):
    """In-memory реализация репозитория записей"""
    
    def __init__(self):
        self._bookings: Dict[int, Booking] = {}
        self._uuid_index: Dict[str, Booking] = {}
        self._client_index: Dict[int, List[Booking]] = {}
        self._date_index: Dict[date, List[Booking]] = {}
        self._next_id = 1
    
    def save(self, booking: Booking) -> Booking:
        """Сохранить запись"""
        if booking.id is None:
            booking.id = self._next_id
            self._next_id += 1
        
        self._bookings[booking.id] = booking
        self._uuid_index[booking.uuid] = booking
        
        # Обновляем индексы
        if booking.client_id:
            if booking.client_id not in self._client_index:
                self._client_index[booking.client_id] = []
            self._client_index[booking.client_id].append(booking)
        
        if booking.booking_date:
            if booking.booking_date not in self._date_index:
                self._date_index[booking.booking_date] = []
            self._date_index[booking.booking_date].append(booking)
        
        return booking
    
    def find_by_id(self, booking_id: int) -> Optional[Booking]:
        """Найти запись по ID"""
        return self._bookings.get(booking_id)
    
    def find_by_uuid(self, uuid: str) -> Optional[Booking]:
        """Найти запись по UUID"""
        return self._uuid_index.get(uuid)
    
    def find_by_client(self, client_id: int) -> List[Booking]:
        """Найти все записи клиента"""
        return self._client_index.get(client_id, [])
    
    def find_by_master(self, master_id: int) -> List[Booking]:
        """Найти все записи мастера"""
        # В in-memory реализации просто фильтруем
        return [b for b in self._bookings.values() if b.master_id == master_id]
    
    def find_by_date(self, target_date: date) -> List[Booking]:
        """Найти записи на конкретную дату"""
        return self._date_index.get(target_date, [])
    
    def find_by_date_range(self, start_date: date, end_date: date) -> List[Booking]:
        """Найти записи в диапазоне дат"""
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date in self._date_index:
                result.extend(self._date_index[current_date])
            current_date = date(current_date.year, current_date.month, current_date.day + 1)
        
        return result
    
    def find_by_status(self, status: BookingStatus) -> List[Booking]:
        """Найти записи по статусу"""
        return [b for b in self._bookings.values() if b.status == status]
    
    def find_conflicting_bookings(
        self,
        master_id: Optional[int],
        booking_date: date,
        start_time: datetime.time,
        end_time: datetime.time,
        exclude_booking_id: Optional[int] = None
    ) -> List[Booking]:
        """Найти конфликтующие записи"""
        conflicts = []
        
        for booking in self._bookings.values():
            # Пропускаем исключенную запись
            if exclude_booking_id and booking.id == exclude_booking_id:
                continue
            
            # Проверяем дату
            if booking.booking_date != booking_date:
                continue
            
            # Проверяем мастера (если указан)
            if master_id is not None and booking.master_id != master_id:
                continue
            
            # Проверяем пересечение времени
            if booking.overlaps_with_time(start_time, end_time):
                conflicts.append(booking)
        
        return conflicts
    
    def update(self, booking: Booking) -> Booking:
        """Обновить запись"""
        if booking.id not in self._bookings:
            raise ValueError(f"Запись с ID {booking.id} не найденa")
        
        old_booking = self._bookings[booking.id]
        
        # Обновляем индексы если изменились данные
        if old_booking.client_id != booking.client_id:
            # Удаляем из старого индекса
            if old_booking.client_id in self._client_index:
                self._client_index[old_booking.client_id] = [
                    b for b in self._client_index[old_booking.client_id] 
                    if b.id != booking.id
                ]
            
            # Добавляем в новый индекс
            if booking.client_id:
                if booking.client_id not in self._client_index:
                    self._client_index[booking.client_id] = []
                self._client_index[booking.client_id].append(booking)
        
        if old_booking.booking_date != booking.booking_date:
            # Удаляем из старой даты
            if old_booking.booking_date in self._date_index:
                self._date_index[old_booking.booking_date] = [
                    b for b in self._date_index[old_booking.booking_date]
                    if b.id != booking.id
                ]
            
            # Добавляем в новую дату
            if booking.booking_date:
                if booking.booking_date not in self._date_index:
                    self._date_index[booking.booking_date] = []
                self._date_index[booking.booking_date].append(booking)
        
        # Сохраняем запись
        self._bookings[booking.id] = booking
        
        return booking
    
    def delete(self, booking_id: int) -> bool:
        """Удалить запись"""
        if booking_id not in self._bookings:
            return False
        
        booking = self._bookings[booking_id]
        
        # Удаляем из индексов
        if booking.uuid in self._uuid_index:
            del self._uuid_index[booking.uuid]
        
        if booking.client_id in self._client_index:
            self._client_index[booking.client_id] = [
                b for b in self._client_index[booking.client_id]
                if b.id != booking_id
            ]
        
        if booking.booking_date in self._date_index:
            self._date_index[booking.booking_date] = [
                b for b in self._date_index[booking.booking_date]
                if b.id != booking_id
            ]
        
        # Удаляем из основного хранилища
        del self._bookings[booking_id]
        
        return True
    
    def count_by_client(self, client_id: int) -> int:
        """Количество записей клиента"""
        return len(self._client_index.get(client_id, []))
    
    def get_upcoming_bookings(self, days_ahead: int = 7) -> List[Booking]:
        """Получить предстоящие записи"""
        today = date.today()
        end_date = date(today.year, today.month, today.day + days_ahead)
        
        return self.find_by_date_range(today, end_date)
