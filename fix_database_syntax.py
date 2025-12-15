# Простой скрипт для исправления синтаксиса
import re

with open('database.py', 'r') as f:
    content = f.read()

# Ищем try: без except в конце функции save_client_record
# Добавляем except если нужно
fixed_content = re.sub(
    r'(def save_client_record.*?return record_id.*?\n)(def load_all_records)',
    r'\1        \n    except Exception as e:\n        print(f"❌ Ошибка сохранения: {e}")\n        return None\n\n\2',
    content,
    flags=re.DOTALL
)

with open('database.py', 'w') as f:
    f.write(fixed_content)

print("✅ Исправлено (попытка)")
