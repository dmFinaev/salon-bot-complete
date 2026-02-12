"""
ENTITY: Запись (Booking)
Entity - имеет идентичность, жизненный цикл, бизнес-правила
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional
from uuid import uuid4

# Импортируем Value Objects и исключения
from ..value_objects.booking_status import BookingStatus
from ..value_objects.service_type import ServiceType
from ..exceptions.booking_exceptions import (
    InvalidBookingTimeException,
    InvalidBookingStatusException,
    BookingCancellationException
)


@dataclass
class Booking:
    """
    Entity: Запись на услугу
    
    Особенности Entity:
    1. Имеет идентификатор (id)
    2. Имеет жизненный цикл (создание, изменение, удаление)
    3. Содержит бизнес-правила
    4. Может изменяться (не frozen)
    """
    
    # Идентификаторы
    id: Optional[int] = None
    uuid: str = field(default_factory=lambda: str(uuid4()))
    
    # Связи (по ID, не по объекту - это важно!)
    client_id: int = None
    master_id: Optional[int] = None
    
    # Value Objects (используем готовые!)
    service: ServiceType = None
    status: BookingStatus = BookingStatus.PENDING
    
    # Дата и время
    booking_date: date = None
    start_time: time = None
    end_time: Optional[time] = None
    
    # Метаданные
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Валидация при создании Entity"""
        self._validate()
        
        # Автоматически вычисляем end_time если не указан
        if self.end_time is None and self.start_time and self.service:
            self._calculate_end_time()
    
    def _validate(self):
        """Валидация бизнес-правил"""
        if not self.booking_date:
            raise InvalidBookingTimeException("Дата записи обязательна")
        
        if not self.start_time:
            raise InvalidBookingTimeException("Время начала обязательно")
        
        if self.booking_date < date.today():
            raise InvalidBookingTimeException("Нельзя записаться на прошедшую дату")
        
        if not self.service:
            raise ValueError("Услуга обязательна")
        
        if not self.client_id:
            raise ValueError("ID клиента обязательно")
    
    def _calculate_end_time(self):
        """Вычисление времени окончания на основе услуги"""
        if not self.start_time or not self.service:
            return
        
        start_datetime = datetime.combine(self.booking_date, self.start_time)
        end_datetime = start_datetime + self.service.duration_minutes
        
        self.end_time = end_datetime.time()
    
    # ========== БИЗНЕС-МЕТОДЫ ==========
    
    def confirm(self):
        """Подтверждение записи (бизнес-правило)"""
        if not self.status.can_transition_to(BookingStatus.CONFIRMED):
            raise InvalidBookingStatusException(
                f"Нельзя подтвердить запись со статусом {self.status}"
            )
        
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now()
    
    def complete(self):
        """Завершение записи (бизнес-правило)"""
        if not self.status.can_transition_to(BookingStatus.COMPLETED):
            raise InvalidBookingStatusException(
                f"Нельзя завершить запись со статусом {self.status}"
            )
        
        self.status = BookingStatus.COMPLETED
        self.updated_at = datetime.now()
    
    def cancel(self, reason: str = ""):
        """Отмена записи (бизнес-правило)"""
        # Проверяем, можно ли отменить
        if not self.status.can_transition_to(BookingStatus.CANCELLED):
            raise BookingCancellationException(
                f"Нельзя отменить запись со статусом {self.status}"
            )
        
        # Проверяем время отмены (минимум за 2 часа)
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        time_until_booking = (booking_datetime - datetime.now()).total_seconds() / 3600
        
        if time_until_booking < 2:
            raise BookingCancellationException(
                "Отмена возможна не менее чем за 2 часа до записи"
            )
        
        self.status = BookingStatus.CANCELLED
        self.notes = f"{self.notes}\nОтменена: {reason}".strip()
        self.updated_at = datetime.now()
    
    def mark_as_no_show(self):
        """Отметка как неявка (бизнес-правило)"""
        if not self.status.can_transition_to(BookingStatus.NO_SHOW):
            raise InvalidBookingStatusException(
                f"Нельзя отметить как неявка со статусом {self.status}"
            )
        
        self.status = BookingStatus.NO_SHOW
        self.updated_at = datetime.now()
    
    def reschedule(self, new_date: date, new_time: time):
        """Перенос записи (бизнес-правило)"""
        if self.status.is_final:
            raise InvalidBookingStatusException(
                f"Нельзя перенести запись с финальным статусом {self.status}"
            )
        
        old_date_time = f"{self.booking_date} {self.start_time}"
        
        self.booking_date = new_date
        self.start_time = new_time
        self.end_time = None  # Сбросим, пересчитается в __post_init__
        
        self.notes = f"{self.notes}\nПеренесено с: {old_date_time}".strip()
        self.updated_at = datetime.now()
        
        # Вызываем __post_init__ для пересчета end_time
        self.__post_init__()
    
    # ========== QUERY METHODS (только возвращают данные) ==========
    
    @property
    def is_active(self) -> bool:
        """Активна ли запись?"""
        return self.status.is_active
    
    @property
    def is_completed(self) -> bool:
        """Завершена ли запись?"""
        return self.status == BookingStatus.COMPLETED
    
    @property
    def is_cancelled(self) -> bool:
        """Отменена ли запись?"""
        return self.status == BookingStatus.CANCELLED
    
    @property
    def formatted_datetime(self) -> str:
        """Форматированная дата и время"""
        return (
            f"{self.booking_date.strftime('%d.%m.%Y')} "
            f"{self.start_time.strftime('%H:%M')}"
        )
    
    @property
    def duration_minutes(self) -> int:
        """Длительность в минутах"""
        return self.service.duration_minutes if self.service else 0
    
    def overlaps_with(self, other: 'Booking') -> bool:
        """Проверяет пересечение по времени с другой записью"""
        if self.booking_date != other.booking_date:
            return False
        
        self_start = datetime.combine(self.booking_date, self.start_time)
        self_end = datetime.combine(self.booking_date, self.end_time or self_start.time())
        
        other_start = datetime.combine(other.booking_date, other.start_time)
        other_end = datetime.combine(other.booking_date, other.end_time or other_start.time())
        
        return not (self_end <= other_start or self_start >= other_end)
    
    def __str__(self) -> str:
        return (
            f"Booking(id={self.id}, "
            f"date={self.formatted_datetime}, "
            f"status={self.status.russian_name}, "
            f"service={self.service.name if self.service else 'N/A'})"
        )
