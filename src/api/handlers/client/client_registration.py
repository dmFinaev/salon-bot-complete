"""
Telegram Handler: Регистрация клиента (обновленная версия)
Теперь использует Service Layer
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from typing import Dict, Any

from src.api.services.client_service import ClientService


class ClientRegistrationHandler:
    """
    Handler для регистрации клиентов через Telegram
    Использует Service Layer для бизнес-логики
    """
    
    # Состояния ConversationHandler
    GET_NAME, GET_PHONE = range(2)
    
    def __init__(self, client_service: ClientService):
        self.client_service = client_service
    
    async def start_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса регистрации"""
        user = update.effective_user
        
        # Проверяем, есть ли уже клиент через сервис
        existing_client = await self.client_service.get_client_by_telegram(str(user.id))
        
        if existing_client:
            await update.message.reply_text(
                f"👋 Добро пожаловать обратно, {existing_client.name}!\n"
                f"Вы уже зарегистрированы в системе.\n\n"
                f"Используйте /menu для доступа к функциям."
            )
            return ConversationHandler.END
        
        # Запрашиваем имя
        await update.message.reply_text(
            "👤 *Регистрация в салоне красоты*\n\n"
            "Для записи на услуги необходимо зарегистрироваться.\n"
            "Пожалуйста, введите ваше имя (например, Анна Иванова):",
            parse_mode='Markdown'
        )
        
        # Сохраняем Telegram ID в context
        context.user_data['telegram_id'] = str(user.id)
        context.user_data['registration_step'] = 'name'
        
        return self.GET_NAME
    
    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение имени от пользователя"""
        name = update.message.text.strip()
        
        # Простая валидация
        if len(name) < 2:
            await update.message.reply_text(
                "❌ Имя должно быть минимум 2 символа.\n"
                "Пожалуйста, введите ваше имя еще раз:"
            )
            return self.GET_NAME
        
        if len(name) > 50:
            await update.message.reply_text(
                "❌ Имя слишком длинное (максимум 50 символов).\n"
                "Пожалуйста, введите более короткое имя:"
            )
            return self.GET_NAME
        
        # Сохраняем имя
        context.user_data['name'] = name
        context.user_data['registration_step'] = 'phone'
        
        await update.message.reply_text(
            f"✅ Отлично, {name}! 📞\n\n"
            "Теперь введите ваш номер телефона для связи:\n"
            "_Можно в любом формате:_\n"
            "• +7 (999) 123-45-67\n"
            "• 89991234567\n"
            "• 9991234567",
            parse_mode='Markdown'
        )
        
        return self.GET_PHONE
    
    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение телефона и сохранение клиента"""
        phone = update.message.text.strip()
        name = context.user_data.get('name')
        telegram_id = context.user_data.get('telegram_id')
        
        # Используем Service Layer для регистрации
        client_dto, is_new, error = await self.client_service.register_client(
            name=name,
            phone=phone,
            telegram_id=telegram_id
        )
        
        if error:
            await update.message.reply_text(
                f"❌ {error}\n"
                "Пожалуйста, введите телефон еще раз:"
            )
            return self.GET_PHONE
        
        # Успешная регистрация
        if is_new:
            message = (
                "🎉 *Регистрация успешно завершена!*\n\n"
                f"✅ *Имя:* {client_dto.name}\n"
                f"✅ *Телефон:* {client_dto.formatted_phone}\n"
                f"✅ *ID клиента:* {client_dto.id}\n\n"
                "Теперь вы можете:\n"
                "• Записываться на услуги (/запись)\n"
                "• Смотреть свои записи (/моизаписи)\n"
                "• Редактировать профиль (/профиль)\n\n"
                "Используйте /menu для главного меню!"
            )
        else:
            message = (
                "🔍 *Вы уже были в нашей системе!*\n\n"
                "Мы обновили ваши данные:\n"
                f"👤 *Имя:* {client_dto.name}\n"
                f"📞 *Телефон:* {client_dto.formatted_phone}\n\n"
                "Добро пожаловать обратно!\n"
                "Используйте /menu для главного меню."
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Очищаем context
        context.user_data.clear()
        
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена регистрации"""
        await update.message.reply_text(
            "❌ Регистрация отменена.\n"
            "Вы можете зарегистрироваться позже командой /start"
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    def get_conversation_handler(self):
        """Создание ConversationHandler для регистрации"""
        return ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start_registration),
                CommandHandler('register', self.start_registration)
            ],
            states={
                self.GET_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)
                ],
                self.GET_PHONE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_phone)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            allow_reentry=True
        )
