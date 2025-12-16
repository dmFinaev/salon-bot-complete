"""
Factory: Создание и конфигурация приложения
Здесь собираем все компоненты вместе
"""

from telegram.ext import Application
from typing import Dict, Any

from src.core.infrastructure.database.repositories.postgres_client_repository import PostgresClientRepository
from src.core.infrastructure.database.repositories.postgres_booking_repository import PostgresBookingRepository

from src.api.services.client_service import ClientService
from src.api.services.booking_service import BookingService

from src.api.handlers.common.main_menu import MainMenuHandler
from src.api.handlers.client.client_registration import ClientRegistrationHandler
from src.api.handlers.booking.booking_creation import BookingCreationHandler
from src.api.handlers.admin.admin_panel import AdminPanelHandler


class ApplicationFactory:
    """Фабрика для создания Telegram бота"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._repositories = {}
        self._services = {}
        self._handlers = []
    
    def build(self) -> Application:
        """Сборка приложения"""
        self._setup_database()
        self._setup_services()
        self._setup_handlers()
        
        return self._create_application()
    
    def _setup_database(self):
        """Настройка базы данных и репозиториев"""
        # TODO: Здесь будет подключение к PostgreSQL
        # Пока используем заглушки
        
        from src.core.infrastructure.database.repositories.in_memory_client_repository import InMemoryClientRepository
        from src.core.infrastructure.database.repositories.in_memory_booking_repository import InMemoryBookingRepository
        
        self._repositories['client'] = InMemoryClientRepository()
        self._repositories['booking'] = InMemoryBookingRepository()
        
        print("✅ Репозитории инициализированы (in-memory)")
    
    def _setup_services(self):
        """Настройка сервисов"""
        self._services['client'] = ClientService(self._repositories['client'])
        self._services['booking'] = BookingService(
            self._repositories['booking'],
            self._repositories['client']
        )
        
        print("✅ Сервисы инициализированы")
    
    def _setup_handlers(self):
        """Настройка обработчиков"""
        # Главное меню
        main_menu = MainMenuHandler(
            client_service=self._services['client'],
            booking_service=self._services['booking']
        )
        self._handlers.extend(main_menu.get_handlers())
        
        # Регистрация клиента
        registration = ClientRegistrationHandler(self._services['client'])
        self._handlers.append(registration.get_conversation_handler())
        
        # Создание записи
        booking_creation = BookingCreationHandler(self._services['booking'])
        self._handlers.append(booking_creation.get_conversation_handler())
        
        # Админ-панель
        admin_panel = AdminPanelHandler(
            client_service=self._services['client'],
            booking_service=self._services['booking']
        )
        self._handlers.extend(admin_panel.get_handlers())
        
        print(f"✅ Загружено {len(self._handlers)} обработчиков")
    
    def _create_application(self) -> Application:
        """Создание Telegram Application"""
        bot_token = self.config.get('BOT_TOKEN')
        
        if not bot_token:
            raise ValueError("BOT_TOKEN не указан в конфигурации")
        
        # Создаем приложение
        application = Application.builder().token(bot_token).build()
        
        # Добавляем все обработчики
        for handler in self._handlers:
            application.add_handler(handler)
        
        # Настраиваем обработку ошибок
        application.add_error_handler(self._error_handler)
        
        print(f"✅ Telegram Application создано")
        return application
    
    async def _error_handler(self, update: object, context):
        """Обработчик ошибок"""
        import logging
        
        logging.error(f"Exception while handling an update: {context.error}")
        
        # Можно отправить сообщение пользователю
        if update and hasattr(update, 'effective_chat'):
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="😕 Произошла ошибка. Пожалуйста, попробуйте позже."
                )
            except:
                pass


def create_app(config: Dict[str, Any]) -> Application:
    """Фабричная функция для создания приложения"""
    factory = ApplicationFactory(config)
    return factory.build()
