"""
EXCEPTIONS: Исключения для домена Booking
Каждое исключение - это конкретная бизнес-ошибка
"""

class BookingException(Exception):
    """Базовое исключение для записей"""
    pass


class InvalidBookingTimeException(BookingException):
    """Некорректное время записи"""
    pass


class BookingTimeConflictException(BookingException):
    """Конфликт времени (уже есть запись на это время)"""
    pass


class InvalidBookingStatusException(BookingException):
    """Некорректный статус записи"""
    pass


class BookingNotFoundException(BookingException):
    """Запись не найдена"""
    pass


class BookingCancellationException(BookingException):
    """Ошибка при отмене записи"""
    pass


class ServiceUnavailableException(BookingException):
    """Услуга недоступна"""
    pass


class MasterUnavailableException(BookingException):
    """Мастер недоступен"""
    pass
