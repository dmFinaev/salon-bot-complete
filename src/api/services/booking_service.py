"""
Service Layer: Сервис для работы с записями
"""

from typing import Optional, Tuple, List, Dict, Any
from datetime import date, time, datetime
from uuid import uuid4

from src.core.application.use_cases.create_booking_use_case import CreateBookingUseCase
from src.core.domain.entities.booking import Booking
from src.core.domain.value_objects.service_type import ServiceType, ServiceCategory
from src.core.domain.exceptions.booking_exceptions import (
    BookingTimeConflictException,
    ServiceUnavailableException
)
from src.api.dtos.booking_dto import BookingDTO
from src.api.dtos.client_dto import ClientDTO


class BookingService:
    """Сервис для операций с записями"""
    
    def __init__(self, booking_repository, client_repository):
        self.booking_repo = booking_repository
        self.client_repo = client_repository
        self.create_use_case = CreateBookingUseCase(
            booking_repository,
            client_repository
        )
    
    async def create_booking(
        self,
        client_id: int,
        service_name: str,
        service_category: str,
        duration_minutes: int,
        price: float,
        booking_date: date,
        start_time: time,
        master_id: Optional[int] = None,
        notes: str = ""
    ) -> Tuple[Optional[BookingDTO], Optional[str]]:
        """
        Создание новой записи
        
        Returns:
            Tuple[booking_dto, error_message]
        """
        try:
            # Создаем Value Object ServiceType
            service = ServiceType(
                name=service_name,
                category=ServiceCategory.from_string(service_category),
                duration_minutes=duration_minutes,
                price_rubles=price
            )
            
            # Используем Use Case
            booking_entity, has_conflicts = self.create_use_case.execute(
                client_id=client_id,
                service=service,
                booking_date=booking_date,
                start_time=start_time,
                master_id=master_id,
                notes=notes
            )
            
            # Конвертируем в DTO
            booking_dto = self._entity_to_dto(booking_entity)
            
            return booking_dto, None
            
        except BookingTimeConflictException as e:
            return None, f"⏰ Время уже занято: {str(e)}"
            
        except ServiceUnavailableException as e:
            return None, f"🔧 Услуга недоступна: {str(e)}"
            
        except Exception as e:
            return None, f"❌ Ошибка: {str(e)}"
    
    async def get_client_bookings(
        self, 
        client_id: int,
        only_active: bool = True
    ) -> List[BookingDTO]:
        """Получение записей клиента"""
        bookings = self.booking_repo.find_by_client(client_id)
        
        if only_active:
            bookings = [b for b in bookings if b.is_active]
        
        # Сортируем по дате (ближайшие первые)
        bookings.sort(key=lambda b: (
            b.booking_date,
            b.start_time if b.start_time else time(0, 0)
        ))
        
        return [self._entity_to_dto(b) for b in bookings]
    
    async def get_booking_by_id(self, booking_id: int) -> Optional[BookingDTO]:
        """Получение записи по ID"""
        booking = self.booking_repo.find_by_id(booking_id)
        
        if not booking:
            return None
        
        return self._entity_to_dto(booking)
    
    async def get_booking_by_uuid(self, uuid: str) -> Optional[BookingDTO]:
        """Получение записи по UUID"""
        booking = self.booking_repo.find_by_uuid(uuid)
        
        if not booking:
            return None
        
        return self._entity_to_dto(booking)
    
    async def cancel_booking(
        self, 
        booking_id: int, 
        reason: str = ""
    ) -> Tuple[bool, Optional[str]]:
        """Отмена записи"""
        booking = self.booking_repo.find_by_id(booking_id)
        
        if not booking:
            return False, "Запись не найдена"
        
        try:
            booking.cancel(reason)
            self.booking_repo.update(booking)
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def confirm_booking(self, booking_id: int) -> Tuple[bool, Optional[str]]:
        """Подтверждение записи"""
        booking = self.booking_repo.find_by_id(booking_id)
        
        if not booking:
            return False, "Запись не найдена"
        
        try:
            booking.confirm()
            self.booking_repo.update(booking)
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    async def reschedule_booking(
        self,
        booking_id: int,
        new_date: date,
        new_time: time
    ) -> Tuple[Optional[BookingDTO], Optional[str]]:
        """Перенос записи"""
        booking = self.booking_repo.find_by_id(booking_id)
        
        if not booking:
            return None, "Запись не найдена"
        
        try:
            booking.reschedule(new_date, new_time)
            updated_booking = self.booking_repo.update(booking)
            
            booking_dto = self._entity_to_dto(updated_booking)
            return booking_dto, None
            
        except Exception as e:
            return None, str(e)
    
    async def get_available_times(
        self,
        target_date: date,
        master_id: Optional[int] = None,
        service_duration: int = 60
    ) -> List[time]:
        """
        Получение доступного времени для записи
        
        Бизнес-правила:
        1. Рабочие часы: 10:00 - 20:00
        2. Перерыв: 14:00 - 15:00
        3. Интервал: 30 минут
        4. Учитывать существующие записи
        """
        available_times = []
        
        # Рабочие часы
        work_start = time(10, 0)
        work_end = time(20, 0)
        
        # Перерыв
        lunch_start = time(14, 0)
        lunch_end = time(15, 0)
        
        # Начинаем с начала рабочего дня
        current = work_start
        
        while current < work_end:
            # Пропускаем обед
            if lunch_start <= current < lunch_end:
                current = lunch_end
                continue
            
            # Проверяем, помещается ли услуга до конца рабочего дня
            end_time = self._add_minutes(current, service_duration)
            
            if end_time > work_end:
                break
            
            # Проверяем, нет ли конфликтующих записей
            has_conflict = self._check_time_conflict(
                target_date=target_date,
                start_time=current,
                end_time=end_time,
                master_id=master_id
            )
            
            if not has_conflict:
                available_times.append(current)
            
            # Следующий слот через 30 минут
            current = self._add_minutes(current, 30)
        
        return available_times
    
    async def get_booking_stats(self, client_id: int) -> Dict[str, Any]:
        """Статистика записей клиента"""
        all_bookings = self.booking_repo.find_by_client(client_id)
        
        stats = {
            "total": len(all_bookings),
            "active": len([b for b in all_bookings if b.is_active]),
            "completed": len([b for b in all_bookings if b.is_completed]),
            "cancelled": len([b for b in all_bookings if b.is_cancelled]),
            "upcoming": [],
            "recent": []
        }
        
        # Предстоящие записи (ближайшие 3)
        upcoming = [b for b in all_bookings if b.is_active]
        upcoming.sort(key=lambda b: (
            b.booking_date,
            b.start_time if b.start_time else time(0, 0)
        ))
        
        stats["upcoming"] = [
            {
                "id": b.id,
                "date": b.booking_date.strftime("%d.%m.%Y") if b.booking_date else "",
                "time": b.start_time.strftime("%H:%M") if b.start_time else "",
                "service": b.service.name if b.service else "",
                "status": b.status.russian_name if hasattr(b.status, 'russian_name') else str(b.status)
            }
            for b in upcoming[:3]
        ]
        
        # Последние записи (последние 5)
        recent = all_bookings[-5:] if len(all_bookings) > 5 else all_bookings
        
        stats["recent"] = [
            {
                "id": b.id,
                "date": b.booking_date.strftime("%d.%m.%Y") if b.booking_date else "",
                "service": b.service.name if b.service else "",
                "status": b.status.russian_name if hasattr(b.status, 'russian_name') else str(b.status)
            }
            for b in recent
        ]
        
        return stats
    
    def _entity_to_dto(self, booking_entity: Booking) -> BookingDTO:
        """Конвертация Entity в DTO"""
        # Получаем имя клиента
        client_name = None
        if booking_entity.client_id:
            client = self.client_repo.find_by_id(booking_entity.client_id)
            if client:
                client_name = client.name
        
        return BookingDTO(
            id=booking_entity.id,
            uuid=booking_entity.uuid,
            client_id=booking_entity.client_id,
            client_name=client_name,
            master_id=booking_entity.master_id,
            service_name=booking_entity.service.name if booking_entity.service else "",
            service_duration=booking_entity.service.duration_minutes if booking_entity.service else 0,
            service_price=booking_entity.service.price_rubles if booking_entity.service else 0.0,
            booking_date=booking_entity.booking_date,
            start_time=booking_entity.start_time,
            end_time=booking_entity.end_time,
            status=booking_entity.status.value if hasattr(booking_entity.status, 'value') else str(booking_entity.status),
            status_russian=booking_entity.status.russian_name if hasattr(booking_entity.status, 'russian_name') else str(booking_entity.status),
            notes=booking_entity.notes,
            created_at=booking_entity.created_at,
            updated_at=booking_entity.updated_at
        )
    
    def _add_minutes(self, t: time, minutes: int) -> time:
        """Добавление минут к времени"""
        total_minutes = t.hour * 60 + t.minute + minutes
        return time(total_minutes // 60, total_minutes % 60)
    
    def _check_time_conflict(
        self,
        target_date: date,
        start_time: time,
        end_time: time,
        master_id: Optional[int] = None
    ) -> bool:
        """Проверка конфликта времени"""
        conflicts = self.booking_repo.find_conflicting_bookings(
            master_id=master_id,
            booking_date=target_date,
            start_time=start_time,
            end_time=end_time
        )
        
        return len(conflicts) > 0
