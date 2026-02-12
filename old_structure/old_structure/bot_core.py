"""
bot_core.py - основная логика Telegram бота
"""
import telebot
from telebot import types
import os
import time
import database as db
import keyboards as kb

# Инициализация бота
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не установлен!")
    print("⚙️ Установите переменную окружения BOT_TOKEN")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Состояния пользователей для многошаговых операций
user_states = {}

# Константы состояний
class UserState:
    ADDING_NAME = "adding_name"
    ADDING_PHONE = "adding_phone"
    ADDING_DATE = "adding_date"
    ADDING_SERVICE = "adding_service"
    EDITING_CHOOSE_FIELD = "editing_choose_field"
    EDITING_ENTER_VALUE = "editing_enter_value"

# ===================== ОБРАБОТЧИКИ КОМАНД =====================

@bot.message_handler(commands=['start'])
def start_command(message):
    """Обработчик команды /start"""
    bot.send_message(message.chat.id,
                    "💇 *Salon Manager* готов к работе!\n"
                    "Выберите действие:",
                    parse_mode=None,
                    reply_markup=kb.main_menu_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    help_text = """
📋 *Доступные команды:*

*/start* - главное меню
*/help* - эта справка
*/edit [номер]* - редактировать запись
*/delete [номер]* - удалить запись

*Через кнопки меню:*
📅 Записать клиента - новая запись
👥 Сегодняшние записи - записи на сегодня
📋 Все записи - все записи с номерами

*Примеры:*
/edit 3 - редактировать запись №3
/delete 2 - удалить запись №2
"""
    bot.send_message(message.chat.id, help_text, parse_mode=None)

# ===================== ГЛАВНОЕ МЕНЮ =====================

@bot.message_handler(func=lambda message: message.text == "📅 Записать клиента")
def start_add_client(message):
    """Начало процесса добавления клиента"""
    user_states[message.chat.id] = {"state": UserState.ADDING_NAME}
    bot.send_message(message.chat.id,
                    "📝 *Начнем запись клиента:*\n\n"
                    "Введите *имя клиента*:",
                    parse_mode=None,
                    reply_markup=kb.cancel_keyboard())

@bot.message_handler(func=lambda message: message.text == "👥 Сегодняшние записи")
def show_today_records(message):
    """Показывает записи на сегодня"""
    records = db.get_today_records()
    
    if not records:
        bot.send_message(message.chat.id, "📝 На сегодня записей нет")
        return
    
    response = "📋 *Записи на сегодня:*\n\n"
    for i, record in enumerate(records, 1):
        client = record["client"]
        response += f"{i}. *{client['name']}*\n"
        response += f"   📅 {client['date']}\n"
        response += f"   ⏰ {client['time']}\n"
        response += f"   📞 {client['phone']}\n"
        response += f"   💇 {client['service']}\n\n"
    
    bot.send_message(message.chat.id, response, parse_mode=None)

@bot.message_handler(func=lambda message: message.text == "📋 Все записи")
def show_all_records(message):
    """Показывает все записи"""
    records = db.load_all_records()
    
    if not records:
        bot.send_message(message.chat.id, "📝 Записей пока нет")
        return
    
    response = "📋 *Все записи:*\n\n"
    for i, record in enumerate(records, 1):
        client = record["client"]
        record_id = record.get("id", "без ID")[:8]
        
    response += f"{i}. *{client['name']}*\n"
    response += f"   📅 {client['date']}\n"
    response += f"   ⏰ {client['time']}\n"
    response += f"   📞 {client['phone']}\n"
    response += f"   💇 {client['service']}\n"
    response += f"   🆔 {record_id}\n\n"
    
    response += "✏️ *Для управления:*\n"
    response += "/edit [номер] - редактировать запись\n"
    response += "/delete [номер] - удалить запись\n"
    response += "Например: `/edit 3` или `/delete 2`"
    
    bot.send_message(message.chat.id, response, parse_mode=None)

# ===================== ДОБАВЛЕНИЕ КЛИЕНТА =====================

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.ADDING_NAME)
def process_client_name(message):
    """Обработка ввода имени клиента"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
        return
    
    user_states[message.chat.id] = {
        "state": UserState.ADDING_PHONE,
        "client": {"name": message.text}
    }
    
    bot.send_message(message.chat.id,
                    f"👤 Имя: *{message.text}*\n\n"
                    "📞 Введите *телефон* клиента:",
                    parse_mode=None)

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.ADDING_PHONE)
def process_client_phone(message):
    """Обработка ввода телефона"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
        return
    
    user_states[message.chat.id]["client"]["phone"] = message.text
    user_states[message.chat.id]["state"] = UserState.ADDING_DATE
    
    bot.send_message(message.chat.id,
                    "📅 Введите *дату и время* (например: 25.12 в 15:00):",
                    parse_mode=None)

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.ADDING_DATE)
def process_client_date(message):
    """Обработка ввода даты"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
        return
    
    user_states[message.chat.id]["client"]["date"] = message.text
    user_states[message.chat.id]["state"] = UserState.ADDING_SERVICE
    
    bot.send_message(message.chat.id,
                    "💇 Введите *услугу* (например: Стрижка, Окрашивание):",
                    parse_mode=None)

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.ADDING_SERVICE)
def process_client_service(message):
    """Обработка ввода услуги и сохранение"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
        return
    
    chat_id = message.chat.id
    client_data = user_states[chat_id]["client"]
    client_data["service"] = message.text
    
    # Сохраняем запись
    record_id = db.save_client_record(chat_id, client_data)
    
    if record_id:
        bot.send_message(chat_id,
                        f"✅ *Клиент записан!*\n\n"
                        f"👤 *Имя:* {client_data['name']}\n"
                        f"📞 *Телефон:* {client_data['phone']}\n"
                        f"📅 *Дата:* {client_data['date']}\n"
                        f"💇 *Услуга:* {client_data['service']}\n\n"
                        f"Запись сохранена!",
                        parse_mode=None,
                        reply_markup=kb.main_menu_keyboard())
    else:
        bot.send_message(chat_id,
                        "❌ Ошибка при сохранении записи",
                        reply_markup=kb.main_menu_keyboard())
    
    # Очищаем состояние
    user_states.pop(chat_id, None)

# ===================== УДАЛЕНИЕ ЗАПИСЕЙ =====================

@bot.message_handler(commands=['delete'])
def delete_record_command(message):
    """Обработчик команды /delete"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            show_delete_help(message.chat.id)
            return
        
        number = int(parts[1])
        records = db.load_all_records()
        
        if number < 1 or number > len(records):
            bot.send_message(message.chat.id,
                           f"⚠️ Нет записи с номером {number}\n"
                           f"Всего записей: {len(records)}")
            return
        
        record = records[number - 1]
        if db.delete_record_by_id(record["id"]):
            bot.send_message(message.chat.id,
                           f"✅ Запись #{number} удалена\n"
                           f"Клиент: *{record['client']['name']}*",
                           parse_mode=None)
        else:
            bot.send_message(message.chat.id, "❌ Ошибка при удалении")
            
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Номер должен быть числом!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

def show_delete_help(chat_id):
    """Показывает справку по команде /delete"""
    bot.send_message(chat_id,
                    "✏️ *Удаление записи:*\n\n"
                    "Используйте: `/delete [номер]`\n"
                    "Например: `/delete 3`\n\n"
                    "Чтобы увидеть номера записей:\n"
                    "Нажмите *📋 Все записи*",
                    parse_mode=None)

# ===================== РЕДАКТИРОВАНИЕ ЗАПИСЕЙ =====================

@bot.message_handler(commands=['edit'])
def edit_record_command(message):
    """Обработчик команды /edit"""
    try:
        parts = message.text.split()
        if len(parts) != 2:
            show_edit_help(message.chat.id)
            return
        
        number = int(parts[1])
        records = db.load_all_records()
        
        if number < 1 or number > len(records):
            bot.send_message(message.chat.id,
                           f"⚠️ Нет записи с номером {number}\n"
                           f"Всего записей: {len(records)}")
            return
        
        record = records[number - 1]
        chat_id = message.chat.id
        
        # Сохраняем данные для редактирования
        user_states[chat_id] = {
            "state": UserState.EDITING_CHOOSE_FIELD,
            "record_id": record["id"],
            "record_number": number,
            "client": record["client"]
        }
        
        bot.send_message(chat_id,
                        f"✏️ *Редактирование записи #{number}:*\n\n"
                        f"👤 {record['client']['name']}\n"
                        f"📞 {record['client']['phone']}\n"
                        f"📅 {record['client']['date']}\n"
                        f"⏰ {record['client']['time']}\n"
                        f"💇 {record['client']['service']}\n\n"
                        f"*Какое поле меняем?*",
                        parse_mode=None,
                        reply_markup=kb.edit_fields_keyboard())
        bot.send_message(message.chat.id, "⚠️ Номер должен быть числом!")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.EDITING_CHOOSE_FIELD)
def process_edit_field_choice(message):
    """Обработка выбора поля для редактирования"""
    chat_id = message.chat.id
    state_data = user_states.get(chat_id, {})
    
    field_map = {
        "👤 Имя": "name",
        "📞 Телефон": "phone",
        "📅 Дата": "date",
        "⏰ Время": "time",
        "💇 Услуга": "service"
    }
    
    if message.text in field_map:
        state_data["field"] = field_map[message.text]
        state_data["field_display"] = message.text
        state_data["state"] = UserState.EDITING_ENTER_VALUE
        user_states[chat_id] = state_data
        
        current_value = state_data["client"][field_map[message.text]]
        bot.send_message(chat_id,
                        f"✏️ Текущее значение: *{current_value}*\n"
                        f"Введите новое значение:",
                        parse_mode=None,
                        reply_markup=kb.cancel_keyboard())
        
    elif message.text == "❌ Отмена":
        cancel_operation(chat_id)
    else:
        bot.send_message(chat_id, "⚠️ Пожалуйста, выберите поле из кнопок")

@bot.message_handler(func=lambda message: 
                    user_states.get(message.chat.id, {}).get("state") == UserState.EDITING_ENTER_VALUE)
def process_edit_new_value(message):
    """Обработка ввода нового значения"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
        return
    
    chat_id = message.chat.id
    state_data = user_states.get(chat_id, {})
    
    if not state_data:
        bot.send_message(chat_id, "❌ Сессия редактирования утеряна")
        return_main_menu(chat_id)
        return
    
    new_value = message.text
    record_id = state_data["record_id"]
    field = state_data["field"]
    field_display = state_data["field_display"]
    record_number = state_data["record_number"]
    
    if db.update_record_field(record_id, field, new_value):
        bot.send_message(chat_id,
                        f"✅ *Запись #{record_number} обновлена!*\n\n"
                        f"Поле: {field_display}\n"
                        f"Новое значение: *{new_value}*",
                        parse_mode=None,
                        reply_markup=kb.main_menu_keyboard())
    else:
        bot.send_message(chat_id, "❌ Ошибка при обновлении записи")
    
    user_states.pop(chat_id, None)

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

def cancel_operation(chat_id):
    """Отменяет текущую операцию"""
    user_states.pop(chat_id, None)
    bot.send_message(chat_id,
                    "❌ Операция отменена",
                    reply_markup=kb.main_menu_keyboard())

def return_main_menu(chat_id):
    """Возвращает в главное меню"""
    user_states.pop(chat_id, None)
    bot.send_message(chat_id,
                    "💇 Возвращаемся в меню...",
                    reply_markup=kb.main_menu_keyboard())

def show_edit_help(chat_id):
    """Показывает справку по команде /edit"""
    bot.send_message(chat_id,
                    "✏️ *Редактирование записи:*\n\n"
                    "Используйте: `/edit [номер]`\n"
                    "Например: `/edit 3`\n\n"
                    "Чтобы увидеть номера записей:\n"
                    "Нажмите *📋 Все записи*",
                    parse_mode=None)

# ===================== ОБРАБОТКА ПРОЧИХ СООБЩЕНИЙ =====================

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработчик всех остальных сообщений"""
    if message.text == "❌ Отмена":
        cancel_operation(message.chat.id)
    else:
        bot.send_message(message.chat.id,
                        "🤔 Не понимаю команду. Используйте кнопки меню или /help",
                        reply_markup=kb.main_menu_keyboard())

# ===================== ЗАПУСК БОТА =====================

def run_bot():
    """Запускает бота"""
    print("🚀 Бот запускается...")
    print(f"🤖 Токен: {'Установлен' if TOKEN else 'НЕ УСТАНОВЛЕН!'}")
    
    while True:
        try:
            print("🔄 Запускаем polling...")
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
            continue
