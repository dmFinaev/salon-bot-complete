"""
UNIT TEST: Тестируем сущность Клиент
"""

import pytest
from src.core.domain.entities.client import Client, PhoneNumber
from src.core.domain.exceptions.client_exceptions import InvalidClientDataException


class TestClientEntity:
    """Тесты для сущности Client"""
    
    def test_create_client_with_valid_data(self):
        """Создание клиента с корректными данными"""
        client = Client(name="Иван Иванов", telegram_id="123456")
        
        assert client.name == "Иван Иванов"
        assert client.telegram_id == "123456"
        assert client.id is None
        assert client.created_at is not None
        assert client.has_telegram() is True
    
    def test_create_client_with_phone(self):
        """Создание клиента с телефоном"""
        phone = PhoneNumber("+7 (999) 123-45-67")
        client = Client(name="Мария", phone=phone)
        
        assert client.phone == phone
        assert client.phone.formatted() == "+7 (999) 123-45-67"
        assert client.can_receive_notifications() is False  # Нет Telegram
    
    def test_create_client_invalid_name(self):
        """Попытка создать клиента с невалидным именем"""
        with pytest.raises(InvalidClientDataException):
            Client(name="")  # Пустое имя
        
        with pytest.raises(InvalidClientDataException):
            Client(name="A")  # Слишком короткое
    
    def test_update_name(self):
        """Обновление имени клиента"""
        client = Client(name="Иван")
        client.update_name("Иван Петров")
        
        assert client.name == "Иван Петров"
        
        with pytest.raises(InvalidClientDataException):
            client.update_name("")  # Нельзя обновить на пустое
    
    def test_phone_validation(self):
        """Валидация номера телефона"""
        # Валидные номера
        valid_numbers = [
            "+7 (999) 123-45-67",
            "79991234567",
            "8 (999) 123-45-67",
            "+7 999 123 45 67"
        ]
        
        for num in valid_numbers:
            phone = PhoneNumber(num)
            assert isinstance(phone, PhoneNumber)
        
        # Невалидные номера
        invalid_numbers = [
            "123",
            "abcdefg",
            "+7 (999) 123-45",
            ""
        ]
        
        for num in invalid_numbers:
            with pytest.raises(ValueError):
                PhoneNumber(num)


class TestPhoneNumberValueObject:
    """Тесты для Value Object PhoneNumber"""
    
    def test_immutability(self):
        """PhoneNumber должен быть неизменяемым"""
        phone = PhoneNumber("+7 (999) 123-45-67")
        
        with pytest.raises(Exception):
            phone.number = "123"  # Попытка изменить
    
    def test_formatted_output(self):
        """Проверка форматирования номера"""
        test_cases = [
            ("79991234567", "+7 (999) 123-45-67"),
            ("+79991234567", "+7 (999) 123-45-67"),
            ("8 (999) 123-45-67", "+7 (999) 123-45-67"),
        ]
        
        for input_num, expected in test_cases:
            phone = PhoneNumber(input_num)
            assert phone.formatted() == expected
    
    def test_equality(self):
        """Два PhoneNumber с одинаковым номером должны быть равны"""
        phone1 = PhoneNumber("+7 (999) 123-45-67")
        phone2 = PhoneNumber("79991234567")
        
        assert phone1 == phone2
        assert hash(phone1) == hash(phone2)
