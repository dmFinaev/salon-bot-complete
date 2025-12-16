"""
DTO (Data Transfer Object): Запись
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, time, datetime


@dataclass
class BookingDTO:
    """DTO для передачи данных о записи"""
    
    id: Optional[int] = None
    uuid: Optional[str] = None
    
    # Связи
    client_id: Optional[int] = None
    client_name: Optional[str] = None  # Для отображения
    master_id: Optional[int] = None
    master_name: Optional[str] = None  # Для отображения
    
    # Данные
    service_name: str = ""
    service_duration: int = 0  # в минутах
    service_price: float = 0.0
    
    # Дата и время
    booking_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    
    # Статус
    status: str = "pending"
    status_russian: str = "Ожидает"
    
    # Метаданные
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def formatted_date(self) -> str:
        """Форматированная дата"""
        if not self.booking_date:
            return "Не указана"
        return self.booking_date.strftime("%d.%m.%Y")
    
    @property
    def formatted_time(self) -> str:
        """Форматированное время"""
        if not self.start_time:
            return "Не указано"
        return self.start_time.strftime("%H:%M")
    
    @property
    def formatted_datetime(self) -> str:
        """Форматированная дата и время"""
        return f"{self.formatted_date} {self.formatted_time}"
    
    @property
    def formatted_duration(self) -> str:
        """Форматированная длительность"""
        hours = self.service_duration // 60
        minutes = self.service_duration % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        return f"{minutes}мин"
    
    @property
    def formatted_price(self) -> str:
        """Форматированная цена"""
        return f"{self.service_price:.2f} ₽"
    
    @property
    def is_active(self) -> bool:
        """Активна ли запись?"""
        return self.status in ["pending", "confirmed"]
    
    @property
    def is_completed(self) -> bool:
        """Завершена ли запись?"""
        return self.status == "completed"
    
    def to_dict(self) -> dict:
        """Конвертация в словарь"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'client_id': self.client_id,
            'client_name': self.client_name,
            'master_id': self.master_id,
            'master_name': self.master_name,
            'service_name': self.service_name,
            'service_duration': self.service_duration,
            'service_price': self.service_price,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'status_russian': self.status_russian,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BookingDTO':
        """Создание из словаря"""
        # Парсим даты
        booking_date = date.fromisoformat(data['booking_date']) if data.get('booking_date') else None
        start_time = time.fromisoformat(data['start_time']) if data.get('start_time') else None
        end_time = time.fromisoformat(data['end_time']) if data.get('end_time') else None
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        
        return cls(
            id=data.get('id'),
            uuid=data.get('uuid'),
            client_id=data.get('client_id'),
            client_name=data.get('client_name'),
            master_id=data.get('master_id'),
            master_name=data.get('master_name'),
            service_name=data.get('service_name', ''),
            service_duration=data.get('service_duration', 0),
            service_price=data.get('service_price', 0.0),
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status=data.get('status', 'pending'),
            status_russian=data.get('status_russian', 'Ожидает'),
            notes=data.get('notes', ''),
            created_at=created_at,
            updated_at=updated_at
        )
