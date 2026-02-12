"""
UNIT TESTS: Тестируем Entity Booking
Пишем тесты для каждой бизнес-функции
"""

import pytest
from datetime import date, time, datetime
from src.core.domain.entities.booking import Booking
from src.core.domain.value_objects.service_type import ServiceType, ServiceCategory
from src.core.domain.value_objects.booking_status import BookingStatus
from src.core.domain.exceptions.booking_exceptions import (
    InvalidBookingTimeException,
    InvalidBookingStatusException,
    BookingCancellationException
)


class TestBookingEntity:
    """Тесты для Entity Booking"""
    
    @pytest.fixture
    def sample_service(self):
        """Фикстура: тестовая услуга"""
        return ServiceType(
            name="Стрижка",
            category=ServiceCategory.HAIR,
            duration_minutes=60,
            price_rubles=1500.00
        )
    
    @pytest.fixture
    def sample_booking(self, sample_service):
        """Фикстура: тестовая запись"""
        return Booking(
            client_id=1,
            service=sample_service,
            booking_date=date(2024, 12, 15),
            start_time=time(14, 0)
        )
    
    def test_create_booking(self, sample_booking):
        """Создание записи"""
        assert sample_booking.client_id == 1
        assert sample_booking.service.name == "Стрижка"
        assert sample_booking.status == BookingStatus.PENDING
        assert sample_booking.is_active is True
        assert sample_booking.uuid is not None
    
    def test_booking_validation(self, sample_service):
        """Валидация при создании"""
        # Должна пройти успешно
        booking = Booking(
            client_id=1,
            service=sample_service,
            booking_date=date(2024, 12, 15),
            start_time=time(14, 0)
        )
        assert booking is not None
        
        # Должна упасть - нет даты
        with pytest.raises(InvalidBookingTimeException):
            Booking(
                client_id=1,
                service=sample_service,
                start_time=time(14, 0)
            )
        
        # Должна упасть - нет времени
        with pytest.raises(InvalidBookingTimeException):
            Booking(
                client_id=1,
                service=sample_service,
                booking_date=date(2024, 12, 15)
            )
    
    def test_confirm_booking(self, sample_booking):
        """Подтверждение записи"""
        sample_booking.confirm()
        
        assert sample_booking.status == BookingStatus.CONFIRMED
        assert sample_booking.updated_at is not None
    
    def test_cannot_confirm_completed_booking(self, sample_booking):
        """Нельзя подтвердить завершенную запись"""
        sample_booking.status = BookingStatus.COMPLETED
        
        with pytest.raises(InvalidBookingStatusException):
            sample_booking.confirm()
    
    def test_cancel_booking(self, sample_booking):
        """Отмена записи"""
        # Устанавливаем будущую дату для теста
        sample_booking.booking_date = date.today()
        
        sample_booking.cancel("Клиент передумал")
        
        assert sample_booking.status == BookingStatus.CANCELLED
        assert "Отменена" in sample_booking.notes
    
    def test_cannot_cancel_less_than_2_hours_before(self, sample_booking):
        """Нельзя отменить менее чем за 2 часа"""
        # Устанавливаем время через 1 час
        now = datetime.now()
        sample_booking.booking_date = now.date()
        sample_booking.start_time = time(now.hour + 1, 0)
        
        with pytest.raises(BookingCancellationException):
            sample_booking.cancel()
    
    def test_reschedule_booking(self, sample_booking):
        """Перенос записи"""
        new_date = date(2024, 12, 20)
        new_time = time(16, 0)
        
        sample_booking.reschedule(new_date, new_time)
        
        assert sample_booking.booking_date == new_date
        assert sample_booking.start_time == new_time
        assert sample_booking.end_time is not None  # Должно вычислиться
        assert "Перенесено" in sample_booking.notes
    
    def test_cannot_reschedule_cancelled_booking(self, sample_booking):
        """Нельзя перенести отмененную запись"""
        sample_booking.status = BookingStatus.CANCELLED
        
        with pytest.raises(InvalidBookingStatusException):
            sample_booking.reschedule(date(2024, 12, 20), time(16, 0))
    
    def test_formatted_datetime(self, sample_booking):
        """Форматирование даты и времени"""
        formatted = sample_booking.formatted_datetime
        
        assert "15.12.2024" in formatted
        assert "14:00" in formatted
    
    def test_overlaps_with(self, sample_service):
        """Проверка пересечения времени"""
        booking1 = Booking(
            client_id=1,
            service=sample_service,
            booking_date=date(2024, 12, 15),
            start_time=time(14, 0)
        )
        
        booking2 = Booking(
            client_id=2,
            service=sample_service,
            booking_date=date(2024, 12, 15),
            start_time=time(14, 30)  # Пересекается!
        )
        
        assert booking1.overlaps_with(booking2) is True
        
        # Разные дни - не пересекаются
        booking2.booking_date = date(2024, 12, 16)
        assert booking1.overlaps_with(booking2) is False


class TestBookingStatusTransitions:
    """Тесты переходов между статусами"""
    
    def test_status_transitions(self):
        """Проверка допустимых переходов"""
        status = BookingStatus.PENDING
        
        # Можно перейти в CONFIRMED или CANCELLED
        assert status.can_transition_to(BookingStatus.CONFIRMED) is True
        assert status.can_transition_to(BookingStatus.CANCELLED) is True
        
        # Нельзя перейти в COMPLETED
        assert status.can_transition_to(BookingStatus.COMPLETED) is False
    
    def test_final_statuses(self):
        """Финальные статусы не могут меняться"""
        final_statuses = [
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
            BookingStatus.NO_SHOW
        ]
        
        for status in final_statuses:
            assert status.is_final is True
            # Нельзя перейти ни в какой другой статус
            for other in BookingStatus:
                assert status.can_transition_to(other) is False
