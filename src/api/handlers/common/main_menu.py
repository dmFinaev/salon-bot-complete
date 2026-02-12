"""
Telegram Handler: Главное меню
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler


class MainMenuHandler:
    """Handler для главного меню бота"""
    
    def __init__(self, client_service, booking_service=None):
        self.client_service = client_service
        self.booking_service = booking_service
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ главного меню"""
        user = update.effective_user
        
        # Проверяем регистрацию
        client = await self.client_service.get_client_by_telegram(str(user.id))
        
        if not client:
            # Если не зарегистрирован - предлагаем регистрацию
            keyboard = [
                [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")],
                [InlineKeyboardButton("ℹ️ О салоне", callback_data="about")]
            ]
            message = (
                "👋 *Добро пожаловать в салон красоты!*\n\n"
                "Для начала работы необходимо зарегистрироваться.\n"
                "Это займет всего пару минут!"
            )
        else:
            # Если зарегистрирован - показываем полное меню
            keyboard = [
                [
                    InlineKeyboardButton("📅 Записаться", callback_data="create_booking"),
                    InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")
                ],
                [
                    InlineKeyboardButton("👤 Профиль", callback_data="profile"),
                    InlineKeyboardButton("🏠 О салоне", callback_data="about")
                ],
                [
                    InlineKeyboardButton("📞 Контакты", callback_data="contacts"),
                    InlineKeyboardButton("🔄 Обновить номер", callback_data="update_phone")
                ]
            ]
            
            message = (
                f"👋 *Привет, {client.name}!*\n\n"
                f"Добро пожаловать в главное меню салона красоты.\n"
                f"Чем могу помочь?"
            )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            await update.callback_query.answer()
        else:
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def handle_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок меню"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        
        if query.data == "register":
            from ..client.client_registration import ClientRegistrationHandler
            handler = ClientRegistrationHandler(self.client_service.client_repo)
            await handler.start_registration(update, context)
            
        elif query.data == "profile":
            client = await self.client_service.get_client_by_telegram(user_id)
            
            if client:
                profile_text = (
                    "👤 *Ваш профиль*\n\n"
                    f"*Имя:* {client.name}\n"
                    f"*Телефон:* {client.formatted_phone}\n"
                    f"*Telegram ID:* {client.telegram_id}\n"
                    f"*Зарегистрирован:* {client.created_at.strftime('%d.%m.%Y') if client.created_at else 'Неизвестно'}\n"
                )
                
                keyboard = [
                    [InlineKeyboardButton("✏️ Изменить имя", callback_data="edit_name")],
                    [InlineKeyboardButton("📞 Изменить телефон", callback_data="edit_phone")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
                ]
                
                await query.edit_message_text(
                    profile_text,
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await query.edit_message_text(
                    "❌ Вы не зарегистрированы в системе.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📝 Зарегистрироваться", callback_data="register")]
                    ])
                )
        
        elif query.data == "about":
            about_text = (
                "💈 *Салон красоты \"Элегант\"*\n\n"
                "📍 *Адрес:* ул. Красоты, 123\n"
                "🕐 *Часы работы:* 10:00 - 20:00\n"
                "📞 *Телефон:* +7 (999) 123-45-67\n\n"
                "*Наши услуги:*\n"
                "• Стрижки и укладки\n"
                "• Окрашивание\n"
                "• Маникюр и педикюр\n"
                "• Косметология\n"
                "• Массаж\n\n"
                "Мы делаем вас красивее каждый день! 💖"
            )
            
            await query.edit_message_text(
                about_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
                ])
            )
        
        elif query.data == "contacts":
            contacts_text = (
                "📞 *Контакты салона*\n\n"
                "*Телефон:* +7 (999) 123-45-67\n"
                "*WhatsApp:* +7 (999) 123-45-67\n"
                "*Email:* salon@elegant.ru\n\n"
                "*Адрес:*\n"
                "ул. Красоты, 123\n"
                "ТЦ \"Гармония\", 3 этаж\n\n"
                "*Как добраться:*\n"
                "🚇 Метро \"Красивая\"\n"
                "🚌 Автобусы: 12, 45, 89\n"
                "🚗 Есть парковка"
            )
            
            await query.edit_message_text(
                contacts_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📍 Открыть карту", url="https://yandex.ru/maps")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")]
                ])
            )
        
        elif query.data == "back_to_menu":
            await self.show_main_menu(update, context)
    
    def get_handlers(self):
        """Получение всех handlers"""
        return [
            CommandHandler(['start', 'menu'], self.show_main_menu),
            CallbackQueryHandler(self.handle_menu_callback, pattern="^(register|profile|about|contacts|back_to_menu|edit_name|edit_phone)$")
        ]
