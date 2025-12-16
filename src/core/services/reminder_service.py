# В импорты
import asyncio
from src.core.services.reminder_service import ReminderService
from src.api.reminders.handlers import setup_reminder_handlers

# В async def main(), после инициализации бота:
db_connection = get_db_connection()  # из вашего database модуля
reminder_service = ReminderService(db_connection, application.bot)
reminder_task = asyncio.create_task(reminder_service.start_scheduler())
setup_reminder_handlers(application)
