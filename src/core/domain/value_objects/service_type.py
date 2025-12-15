"""
VALUE OBJECT: Тип услуги (стрижка, окрашивание и т.д.)
Value Object - неизменяемый, не имеет ID, определяется своими атрибутами
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ServiceCategory(Enum):
    """Категории услуг"""
    HAIR = "hair"
    NAILS = "nails"
    COSMETOLOGY = "cosmetology"
    MASSAGE = "massage"
    OTHER = "other"
    
    @classmethod
    def from_string(cls, value: str) -> 'ServiceCategory':
        """Создание из строки"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.OTHER


@dataclass(frozen=True)  # frozen=True делает объект неизменяемым
class ServiceType:
    """
    Value Object: Тип услуги
    
    Особенности Value Object:
    1. Нет идентификатора (ID)
    2. Неизменяемый (immutable)
    3. Равенство по значениям, а не по ссылке
    4. Может использоваться в разных Entity
    """
    
    name: str
    category: ServiceCategory
    duration_minutes: int
    price_rubles: float
    description: Optional[str] = None
    
    def __post_init__(self):
        """Валидация при создании"""
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Название услуги должно быть минимум 2 символа")
        
        if self.duration_minutes <= 0:
            raise ValueError("Длительность должна быть положительной")
        
        if self.price_rubles < 0:
            raise ValueError("Цена не может быть отрицательной")
    
    @property
    def formatted_price(self) -> str:
        """Форматированная цена"""
        return f"{self.price_rubles:.2f} ₽"
    
    @property
    def formatted_duration(self) -> str:
        """Форматированная длительность"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        return f"{minutes}мин"
    
    def is_available_at_time(self, start_hour: int, end_hour: int) -> bool:
        """Проверка, доступна ли услуга в указанное время"""
        # Простая проверка - услуга должна укладываться в рабочий день
        total_hours = self.duration_minutes / 60
        return (end_hour - start_hour) >= total_hours
    
    def __eq__(self, other: object) -> bool:
        """Два ServiceType равны, если все поля равны"""
        if not isinstance(other, ServiceType):
            return False
        
        return (
            self.name == other.name and
            self.category == other.category and
            self.duration_minutes == other.duration_minutes and
            self.price_rubles == other.price_rubles and
            self.description == other.description
        )
    
    def __hash__(self) -> int:
        """Hash для использования в словарях и множествах"""
        return hash((
            self.name,
            self.category.value,
            self.duration_minutes,
            self.price_rubles,
            self.description
        ))
    
    def __str__(self) -> str:
        return f"{self.name} ({self.formatted_duration}) - {self.formatted_price}"
