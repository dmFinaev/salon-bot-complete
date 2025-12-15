"""
keyboards.py - все клавиатуры бота
"""
from telebot import types

def main_menu_keyboard():
    """Главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📅 Записать клиента")
    btn2 = types.KeyboardButton("👥 Сегодняшние записи")
    btn3 = types.KeyboardButton("📋 Все записи")
    markup.add(btn1, btn2, btn3)
    return markup

def cancel_keyboard():
    """Клавиатура с кнопкой Отмена"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("❌ Отмена")
    markup.add(btn)
    return markup

def edit_fields_keyboard():
    """Клавиатура для выбора поля при редактировании"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👤 Имя")
    btn2 = types.KeyboardButton("📞 Телефон")
    btn3 = types.KeyboardButton("📅 Дата")
    btn4 = types.KeyboardButton("⏰ Время")
    btn5 = types.KeyboardButton("💇 Услуга")
    btn6 = types.KeyboardButton("❌ Отмена")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    return markup
