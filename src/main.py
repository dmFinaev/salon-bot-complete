"""
Главный файл Telegram бота
Точка входа в приложение
"""

import asyncio
import logging
from typing import Dict, Any

from src.api.factory import create_app


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def load_config() -> Dict[str, Any]:
    """Загрузка конфигурации"""
    import os
    
    config = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN', ''),
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///salon.db'),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'TIMEZONE': os.getenv('TZ', 'Europe/Samara'),
    }
    
    # Проверяем обязательные параметры
    if not config['BOT_TOKEN']:
        logger.error("❌ BOT_TOKEN не установлен!")
        logger.info("⚙️ Установите переменную окружения BOT_TOKEN")
        raise ValueError("BOT_TOKEN не установлен")
    
    logger.info(f"✅ Конфигурация загружена")
    logger.info(f"   Timezone: {config['TIMEZONE']}")
    logger.info(f"   Log level: {config['LOG_LEVEL']}")
    
    return config


async def main():
    """Основная функция"""
    logger.info("🚀 Запуск Telegram бота салона красоты...")
    
    try:
        # Загружаем конфигурацию
        config = load_config()
        
        # Создаем приложение через фабрику
        application = create_app(config)
        
        logger.info("✅ Приложение создано")
        logger.info("🤖 Бот запускается...")
        
        # Запускаем бота
        await application.run_polling()
        
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        
    finally:
        logger.info("🛑 Бот завершил работу")


if __name__ == '__main__':
    asyncio.run(main())
