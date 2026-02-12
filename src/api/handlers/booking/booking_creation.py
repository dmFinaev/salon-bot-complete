"""
Telegram Handler: Создание записи
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from datetime import date, time, datetime
from typing import Dict, Any, List
import calendar

from src.api.services.booking_service import BookingService
from src.api.services.client_service import ClientService


class BookingCreationHandler:
    """
    Handler для создания записи через Telegram
    
    Flow:
    1. Выбор услуги
    2. Выбор даты
    3. Выбор времени
    4. Подтверждение
    """
    
    # Состояния ConversationHandler
    SELECT_SERVICE, SELECT_DATE, SELECT_TIME, CONFIRM_BOOKING = range(4)
    
    # Каталог услуг (временный, потом из БД)
    SERVICES = [
        {
            "id": 1,
            "name": "💇‍♀️ Стрижка женская",
            "category": "hair",
            "duration": 60,
            "price": 1500.00,
            "description": "Стрижка, укладка, консультация стилиста"
        },
        {
            "id": 2,
            "name": "💇‍♂️ Стрижка мужская",
            "category": "hair",
            "duration": 30,
            "price": 800.00,
            "description": "Стрижка машинкой или ножницами"
        },
        {
            "id": 3,
            "name": "💅 Маникюр классический",
            "category": "nails",
            "duration": 90,
            "price": 1200.00,
            "description": "Обработка ногтей, маникюр, покрытие"
        },
        {
            "id": 4,
            "name": "💆‍♀️ Массаж лица",
            "category": "cosmetology",
            "duration": 60,
            "price": 2000.00,
            "description": "Расслабляющий массаж, уход за кожей"
        },
        {
            "id": 5,
            "name": "✨ Окрашивание волос",
            "category": "hair",
            "duration": 120,
            "price": 3500.00,
            "description": "Окрашивание, тонирование, уход"
        },
    ]
    
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service
    
    async def start_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало процесса создания записи"""
        user = update.effective_user
        
        # Проверяем регистрацию клиента
        # TODO: получить client_service из context
        # client = await self.client_service.get_client_by_telegram(str(user.id))
        # if not client:
        #     await update.message.reply_text(
        #         "❌ Вы не зарегистрированы!\n"
        #         "Сначала зарегистрируйтесь командой /start"
        #     )
        #     return ConversationHandler.END
        
        # Пока используем заглушку
        context.user_data['client_id'] = 1  # TODO: заменить на реальный ID
        
        # Показываем услуги
        keyboard = []
        for service in self.SERVICES:
            button_text = f"{service['name']} - {service['price']:.0f}₽"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"service_{service['id']}")])
        
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
        
        await update.message.reply_text(
            "💈 *Выберите услугу:*\n\n"
            "_Нажмите на услугу для выбора_",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return self.SELECT_SERVICE
    
    async def select_service(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор услуги"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Создание записи отменено.")
            context.user_data.clear()
            return ConversationHandler.END
        
        if query.data.startswith("service_"):
            service_id = int(query.data.split("_")[1])
            
            # Находим услугу
            service = next((s for s in self.SERVICES if s["id"] == service_id), None)
            
            if not service:
                await query.edit_message_text("❌ Услуга не найдена.")
                return ConversationHandler.END
            
            # Сохраняем выбранную услугу
            context.user_data['selected_service'] = service
            context.user_data['service_id'] = service_id
            
            # Показываем описание услуги
            await query.edit_message_text(
                f"✅ *Выбрана услуга:* {service['name']}\n\n"
                f"📝 *Описание:* {service['description']}\n"
                f"⏰ *Длительность:* {service['duration']} мин\n"
                f"💰 *Цена:* {service['price']:.0f}₽\n\n"
                "📅 *Теперь выберите дату записи:*\n"
                "_Используйте кнопки для навигации_",
                parse_mode='Markdown',
                reply_markup=self._create_calendar_keyboard()
            )
            
            return self.SELECT_DATE
    
    async def select_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор даты"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Создание записи отменено.")
            context.user_data.clear()
            return ConversationHandler.END
        
        if query.data == "today":
            selected_date = date.today()
        elif query.data == "tomorrow":
            selected_date = date.today().replace(day=date.today().day + 1)
        elif query.data.startswith("date_"):
            # date_2024-12-20
            date_str = query.data.split("_")[1]
            selected_date = date.fromisoformat(date_str)
        elif query.data.startswith("nav_"):
            # Обработка навигации по календарю
            # nav_2024-12 (месяц и год)
            nav_data = query.data.split("_")[1]
            year, month = map(int, nav_data.split("-"))
            
            await query.edit_message_text(
                "📅 Выберите дату:",
                reply_markup=self._create_calendar_keyboard(year, month)
            )
            return self.SELECT_DATE
        else:
            await query.edit_message_text("❌ Неверный выбор даты.")
            return self.SELECT_DATE
        
        # Проверяем что дата не в прошлом
        if selected_date < date.today():
            await query.edit_message_text(
                "❌ Нельзя записаться на прошедшую дату!\n"
                "Выберите другую дату:",
                reply_markup=self._create_calendar_keyboard()
            )
            return self.SELECT_DATE
        
        # Сохраняем дату
        context.user_data['selected_date'] = selected_date
        
        # Получаем доступное время
        service = context.user_data.get('selected_service')
        available_times = await self.booking_service.get_available_times(
            target_date=selected_date,
            service_duration=service['duration'] if service else 60
        )
        
        if not available_times:
            await query.edit_message_text(
                f"❌ На {selected_date.strftime('%d.%m.%Y')} нет свободного времени.\n"
                "Выберите другую дату:",
                reply_markup=self._create_calendar_keyboard()
            )
            return self.SELECT_DATE
        
        # Создаем клавиатуру с временем
        keyboard = []
        row = []
        
        for i, t in enumerate(available_times):
            time_str = t.strftime("%H:%M")
            row.append(InlineKeyboardButton(time_str, callback_data=f"time_{time_str}"))
            
            if len(row) == 3 or i == len(available_times) - 1:
                keyboard.append(row)
                row = []
        
        keyboard.append([InlineKeyboardButton("⬅️ Назад к датам", callback_data="back_to_date")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
        
        await query.edit_message_text(
            f"📅 *Дата:* {selected_date.strftime('%d.%m.%Y (%A)')}\n\n"
            f"⏰ *Выберите время:*\n"
            f"_Доступные слоты:_",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        return self.SELECT_TIME
    
    async def select_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор времени"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Создание записи отменено.")
            context.user_data.clear()
            return ConversationHandler.END
        
        if query.data == "back_to_date":
            await query.edit_message_text(
                "📅 Выберите дату:",
                reply_markup=self._create_calendar_keyboard()
            )
            return self.SELECT_DATE
        
        if query.data.startswith("time_"):
            time_str = query.data.split("_")[1]
            selected_time = time.fromisoformat(time_str)
            
            # Сохраняем время
            context.user_data['selected_time'] = selected_time
            
            # Показываем подтверждение
            service = context.user_data.get('selected_service')
            selected_date = context.user_data.get('selected_date')
            
            if not service or not selected_date:
                await query.edit_message_text("❌ Ошибка данных. Начните заново.")
                context.user_data.clear()
                return ConversationHandler.END
            
            # Вычисляем время окончания
            start_datetime = datetime.combine(selected_date, selected_time)
            end_datetime = start_datetime.replace(minute=start_datetime.minute + service['duration'])
            
            confirmation_text = (
                f"✅ *ПОДТВЕРЖДЕНИЕ ЗАПИСИ*\n\n"
                f"💈 *Услуга:* {service['name']}\n"
                f"📝 *Описание:* {service['description']}\n"
                f"📅 *Дата:* {selected_date.strftime('%d.%m.%Y (%A)')}\n"
                f"⏰ *Время:* {selected_time.strftime('%H:%M')} - {end_datetime.time().strftime('%H:%M')}\n"
                f"⏱️ *Длительность:* {service['duration']} мин\n"
                f"💰 *Цена:* {service['price']:.0f}₽\n\n"
                f"📍 *Адрес салона:* ул. Красоты, 123\n"
                f"📞 *Телефон:* +7 (999) 123-45-67\n\n"
                f"Всё верно?"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Да, записаться", callback_data="confirm"),
                    InlineKeyboardButton("✏️ Изменить время", callback_data="back_to_time")
                ],
                [
                    InlineKeyboardButton("📅 Изменить дату", callback_data="back_to_date"),
                    InlineKeyboardButton("💈 Изменить услугу", callback_data="back_to_service")
                ],
                [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
            ]
            
            await query.edit_message_text(
                confirmation_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            return self.CONFIRM_BOOKING
    
    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение и создание записи"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "cancel":
            await query.edit_message_text("❌ Создание записи отменено.")
            context.user_data.clear()
            return ConversationHandler.END
        
        if query.data in ["back_to_service", "back_to_date", "back_to_time"]:
            if query.data == "back_to_service":
                # Возврат к выбору услуги
                keyboard = []
                for service in self.SERVICES:
                    button_text = f"{service['name']} - {service['price']:.0f}₽"
                    keyboard.append([InlineKeyboardButton(button_text, callback_data=f"service_{service['id']}")])
                
                keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
                
                await query.edit_message_text(
                    "💈 *Выберите услугу:*",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return self.SELECT_SERVICE
                
            elif query.data == "back_to_date":
                await query.edit_message_text(
                    "📅 Выберите дату:",
                    reply_markup=self._create_calendar_keyboard()
                )
                return self.SELECT_DATE
                
            elif query.data == "back_to_time":
                # Возврат к выбору времени
                selected_date = context.user_data.get('selected_date')
                service = context.user_data.get('selected_service')
                
                if not selected_date or not service:
                    await query.edit_message_text("❌ Ошибка данных.")
                    context.user_data.clear()
                    return ConversationHandler.END
                
                available_times = await self.booking_service.get_available_times(
                    target_date=selected_date,
                    service_duration=service['duration']
                )
                
                keyboard = []
                row = []
                
                for i, t in enumerate(available_times):
                    time_str = t.strftime("%H:%M")
                    row.append(InlineKeyboardButton(time_str, callback_data=f"time_{time_str}"))
                    
                    if len(row) == 3 or i == len(available_times) - 1:
                        keyboard.append(row)
                        row = []
                
                keyboard.append([InlineKeyboardButton("⬅️ Назад к датам", callback_data="back_to_date")])
                keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])
                
                await query.edit_message_text(
                    f"📅 *Дата:* {selected_date.strftime('%d.%m.%Y')}\n\n"
                    f"⏰ *Выберите время:*",
                    parse_mode='Markdown',
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
                return self.SELECT_TIME
        
        if query.data == "confirm":
            # Создаем запись
            client_id = context.user_data.get('client_id', 1)  # TODO: реальный ID
            service = context.user_data.get('selected_service')
            selected_date = context.user_data.get('selected_date')
            selected_time = context.user_data.get('selected_time')
            
            if not all([client_id, service, selected_date, selected_time]):
                await query.edit_message_text("❌ Недостаточно данных для создания записи.")
                context.user_data.clear()
                return ConversationHandler.END
            
            # Создаем запись через сервис
            booking_dto, error = await self.booking_service.create_booking(
                client_id=client_id,
                service_name=service['name'],
                service_category=service['category'],
                duration_minutes=service['duration'],
                price=service['price'],
                booking_date=selected_date,
                start_time=selected_time
            )
            
            if error:
                await query.edit_message_text(f"❌ Ошибка создания записи: {error}")
                context.user_data.clear()
                return ConversationHandler.END
            
            # Успех!
            success_text = (
                f"🎉 *ЗАПИСЬ СОЗДАНА!*\n\n"
                f"📋 *Детали записи:*\n"
                f"🆔 *Номер:* {booking_dto.id}\n"
                f"🔑 *Код:* {booking_dto.uuid[:8].upper()}\n"
                f"💈 *Услуга:* {booking_dto.service_name}\n"
                f"📅 *Дата:* {booking_dto.formatted_date}\n"
                f"⏰ *Время:* {booking_dto.formatted_time}\n"
                f"⏱️ *Длительность:* {booking_dto.formatted_duration}\n"
                f"💰 *Цена:* {booking_dto.formatted_price}\n"
                f"📊 *Статус:* {booking_dto.status_russian}\n\n"
                f"📍 *Адрес:* ул. Красоты, 123\n"
                f"📞 *Телефон:* +7 (999) 123-45-67\n\n"
                f"⏰ *Пожалуйста, приходите за 10 минут до записи.*\n"
                f"📱 *Мы напомним вам за день до визита!*\n\n"
                f"Используйте /моизаписи для просмотра всех записей."
            )
            
            keyboard = [
                [InlineKeyboardButton("📋 Мои записи", callback_data="my_bookings")],
                [InlineKeyboardButton("📅 Новая запись", callback_data="new_booking")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
            
            await query.edit_message_text(
                success_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # Очищаем данные
            context.user_data.clear()
            
            return ConversationHandler.END
    
    def _create_calendar_keyboard(self, year=None, month=None) -> InlineKeyboardMarkup:
        """Создание клавиатуры календаря"""
        now = datetime.now()
        if not year:
            year = now.year
        if not month:
            month = now.month
        
        # Заголовок календаря
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]
        
        # Кнопки навигации
        keyboard = []
        
        # Заголовок с навигацией
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        
        header_row = [
            InlineKeyboardButton("◀️", callback_data=f"nav_{prev_year}-{prev_month:02d}"),
            InlineKeyboardButton(f"{month_names[month-1]} {year}", callback_data="current"),
            InlineKeyboardButton("▶️", callback_data=f"nav_{next_year}-{next_month:02d}")
        ]
        keyboard.append(header_row)
        
        # Дни недели
        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        keyboard.append([InlineKeyboardButton(day, callback_data="ignore") for day in days_of_week])
        
        # Дни месяца
        cal = calendar.monthcalendar(year, month)
        today = date.today()
        
        for week in cal:
            row = []
            for day in week:
                if day == 0:
                    row.append(InlineKeyboardButton(" ", callback_data="ignore"))
                else:
                    current_date = date(year, month, day)
                    
                    # Проверяем, не прошедшая ли дата
                    if current_date < today:
                        row.append(InlineKeyboardButton(f"❌", callback_data="ignore"))
                    else:
                        date_str = current_date.isoformat()
                        row.append(InlineKeyboardButton(str(day), callback_data=f"date_{date_str}"))
            
            keyboard.append(row)
        
        # Быстрые кнопки
        quick_buttons = [
            InlineKeyboardButton("Сегодня", callback_data="today"),
            InlineKeyboardButton("Завтра", callback_data="tomorrow"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
        keyboard.append(quick_buttons)
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_conversation_handler(self):
        """Создание ConversationHandler"""
        return ConversationHandler(
            entry_points=[
                CommandHandler(['запись', 'booking', 'newbooking'], self.start_booking),
                CallbackQueryHandler(self.start_booking, pattern="^new_booking$")
            ],
            states={
                self.SELECT_SERVICE: [
                    CallbackQueryHandler(self.select_service, pattern="^(service_\\d+|cancel)$")
                ],
                self.SELECT_DATE: [
                    CallbackQueryHandler(self.select_date, pattern="^(date_.+|today|tomorrow|nav_.+|cancel)$")
                ],
                self.SELECT_TIME: [
                    CallbackQueryHandler(self.select_time, pattern="^(time_.+|back_to_date|cancel)$")
                ],
                self.CONFIRM_BOOKING: [
                    CallbackQueryHandler(self.confirm_booking, pattern="^(confirm|back_to_service|back_to_date|back_to_time|cancel)$")
                ]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)],
            allow_reentry=True
        )
    
    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена"""
        await update.message.reply_text("❌ Создание записи отменено.")
        context.user_data.clear()
        return ConversationHandler.END
