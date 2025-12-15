with open('bot_core.py', 'r') as f:
    content = f.read()

# Упрощаем форматирование - убираем часть звездочек
old_text = '''    response = "📋 *Все записи:*\\\\n\\\\n"
    for i, record in enumerate(records, 1):
        client = record["client"]
        record_id = record.get("id", "без ID")[:8]

        response += f"{i}. *{client['name']}*\\\\n"
        response += f"   📅 {client['date']}\\\\n"
        response += f"   ⏰ {client['time']}\\\\n"
        response += f"   📞 {client['phone']}\\\\n"
        response += f"   💇 {client['service']}\\\\n"
        response += f"   🆔 {record_id}\\\\n\\\\n"

    response += "✏️ *Для управления:*\\\\n"
    response += "/edit [номер] - редактировать запись\\\\n"
    response += "/delete [номер] - удалить запись\\\\n"
    response += "Например: `/edit 3` или `/delete 2`"'''

new_text = '''    response = "📋 *Все записи:*\\\\n\\\\n"
    for i, record in enumerate(records, 1):
        client = record["client"]
        record_id = record.get("id", "без ID")[:8]

        response += f"{i}. {client['name']}\\\\n"
        response += f"   📅 {client['date']}\\\\n"
        response += f"   ⏰ {client['time']}\\\\n"
        response += f"   📞 {client['phone']}\\\\n"
        response += f"   💇 {client['service']}\\\\n"
        response += f"   🆔 {record_id}\\\\n\\\\n"

    response += "✏️ Для управления:\\\\n"
    response += "/edit [номер] - редактировать запись\\\\n"
    response += "/delete [номер] - удалить запись\\\\n"
    response += "Например: /edit 3 или /delete 2"'''

content = content.replace(old_text, new_text)

with open('bot_core.py', 'w') as f:
    f.write(content)
print("✅ Markdown форматирование упрощено")
