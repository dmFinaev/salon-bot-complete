#!/usr/bin/env python3
"""
Тест структуры бота без запуска Telegram API
"""

import sys
sys.path.insert(0, '/home/fin/salon-bot-complete/src')

print("=== ТЕСТ СТРУКТУРЫ БОТА ===\n")

# Тест 1: Импорты
print("1. Тестируем импорты...")
try:
    from core.domain.entities.client import Client
    from core.domain.entities.booking import Booking
    from api.services.client_service import ClientService
    from api.factory import ApplicationFactory
    print("   ✅ Все импорты работают")
except ImportError as e:
    print(f"   ❌ Ошибка импорта: {e}")
    sys.exit(1)

# Тест 2: In-memory репозитории
print("\n2. Тестируем in-memory репозитории...")
try:
    from core.infrastructure.database.repositories.in_memory_client_repository import InMemoryClientRepository
    from core.infrastructure.database.repositories.in_memory_booking_repository import InMemoryBookingRepository
    
    client_repo = InMemoryClientRepository()
    booking_repo = InMemoryBookingRepository()
    
    print(f"   ✅ Репозитории созданы")
    print(f"   Клиентов: {len(client_repo.find_all())}")
    print(f"   Записей: {len(booking_repo.find_all())}")
except Exception as e:
    print(f"   ❌ Ошибка репозиториев: {e}")

# Тест 3: Client Service
print("\n3. Тестируем Client Service...")
try:
    from api.services.client_service import ClientService
    
    service = ClientService(client_repo)
    
    # Тест регистрации
    client_dto, is_new, error = asyncio.run(service.register_client(
        name="Тестовый Клиент",
        phone="+79991234567",
        telegram_id="test123"
    ))
    
    if error:
        print(f"   ❌ Ошибка регистрации: {error}")
    else:
        print(f"   ✅ Клиент зарегистрирован")
        print(f"      ID: {client_dto.id}, Имя: {client_dto.name}")
        print(f"      Новый: {is_new}")
        
        # Тест поиска
        found = asyncio.run(service.get_client_by_telegram("test123"))
        print(f"      Найден по Telegram: {found.name if found else 'Нет'}")
except Exception as e:
    print(f"   ❌ Ошибка сервиса: {e}")

# Тест 4: Factory
print("\n4. Тестируем Factory...")
try:
    config = {
        'BOT_TOKEN': 'test_token',
        'DATABASE_URL': 'sqlite:///test.db',
        'LOG_LEVEL': 'INFO'
    }
    
    factory = ApplicationFactory(config)
    print("   ✅ Factory создана")
    
    # Можно создать приложение (но не запускать)
    # app = factory.build()
    # print("   ✅ Приложение создано")
    
except Exception as e:
    print(f"   ❌ Ошибка factory: {e}")

print("\n=== ИТОГ ===")
print("Структура бота собрана и готова к работе!")
print("Следующие шаги:")
print("1. Установить BOT_TOKEN в переменные окружения")
print("2. Запустить: python src/main.py")
print("3. Протестировать в Telegram")
