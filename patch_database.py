import re

with open('database.py', 'r') as f:
    lines = f.readlines()

# Находим где начинается save_client_record
start_line = None
for i, line in enumerate(lines):
    if 'def save_client_record' in line:
        start_line = i
        break

if start_line is not None:
    # Находим где должна закончиться функция
    for i in range(start_line, len(lines)):
        if i > start_line + 50:  # Ищем в пределах 50 строк
            break
        if lines[i].strip().startswith('def '):  # Следующая функция
            # Вставляем закрывающие блоки перед следующей функцией
            closing_blocks = [
                '        conn.commit()\n',
                '        conn.close()\n',
                '        \n',
                '        print(f"✅ Запись сохранена с ID: {record_id}")\n',
                '        return record_id\n',
                '        \n',
                '    except Exception as e:\n',
                '        print(f"❌ Ошибка сохранения: {e}")\n',
                '        return None\n'
            ]
            
            # Вставляем перед следующей функцией
            lines = lines[:i] + closing_blocks + lines[i:]
            break
    
    with open('database.py', 'w') as f:
        f.writelines(lines)
    print("✅ Функция save_client_record исправлена")
else:
    print("❌ Функция save_client_record не найдена")
