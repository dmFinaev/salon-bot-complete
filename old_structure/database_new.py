"""
database.py - работа с SQLite базой данных
"""
import sqlite3
import datetime
import uuid
import os
from typing import List, Dict, Optional

def get_connection():
    """Создает подключение к базе данных"""
    db_path = os.path.join('data', 'salon_bot.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Инициализирует таблицы в базе данных"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Таблица записей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            chat_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            service TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            reminder_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица статуса напоминаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders_status (
            record_id TEXT PRIMARY KEY,
            day_before_sent INTEGER DEFAULT 0,
            two_hours_before_sent INTEGER DEFAULT 0,
            FOREIGN KEY (record_id) REFERENCES appointments (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def generate_record_id():
    """Генерирует уникальный ID для записи"""
    return "rec_" + str(uuid.uuid4())[:8]

def save_client_record(chat_id: int, client_data: Dict) -> Optional[str]:
    """
    Сохраняет запись клиента в базу данных
    Возвращает ID созданной записи или None при ошибке
    """
    try:
        record_id = generate_record_id()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (id, chat_id, name, phone, service, appointment_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            record_id,
            chat_id,
            client_data.get('name', ''),
            client_data.get('phone', ''),
            client_data.get('service', ''),
            client_data.get('date', '') + ' ' + client_data.get('time', '')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Запись сохранена с ID: {record_id}")
        return record_id
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return None

def load_all_records() -> List[Dict]:
    """Загружает ВСЕ записи из базы данных"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, chat_id, name, phone, service, appointment_date, reminder_sent
            FROM appointments
            ORDER BY created_at DESC
        ''')
        
        records = []
        for row in cursor.fetchall():
            # Парсим дату и время
            date_time = row['appointment_date'].split(' ')
            date_part = date_time[0] if len(date_time) > 0 else ''
            time_part = date_time[1] if len(date_time) > 1 else ''
            
            records.append({
                'id': row['id'],
                'chat_id': row['chat_id'],
                'client': {
                    'name': row['name'],
                    'phone': row['phone'],
                    'service': row['service'],
                    'date': date_part,
                    'time': time_part
                },
                'reminder_sent': row['reminder_sent']
            })
        
        conn.close()
        return records
        
    except Exception as e:
        print(f"❌ Ошибка чтения из базы: {e}")
        return []

# Инициализируем базу при импорте
init_database()
