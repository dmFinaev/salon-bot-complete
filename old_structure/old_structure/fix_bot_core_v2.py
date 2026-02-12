with open('bot_core.py', 'r') as f:
    content = f.read()

# Заменяем проблемную часть
old_text = '''        bot.send_message(chat_id,
                        f"✏️ *Редактирование записи #{number}:*\\\\n\\\\n"
                        f"👤 {record[\\"client\\"][\\"name\\"]}\\\\n"
                        f"📞 {record[\\"client\\"][\\"phone\\"]}\\\\n"
                        f"📅 {record[\\"client\\"][\\"date\\"]}\\\\n"
                        f"⏰ {record[\\"client\\"][\\"time\\"]}\\\\n"
                        f"💇 {record[\\"client\\"][\\"service\\"]}\\\\n\\\\n"
                        f"*Какое поле меняем?*",
                        parse_mode='Markdown',
                        reply_markup=kb.edit_fields_keyboard())'''

new_text = '''        bot.send_message(chat_id,
                        f"✏️ *Редактирование записи #{number}:*\\n\\n"
                        f"👤 {record['client']['name']}\\n"
                        f"📞 {record['client']['phone']}\\n"
                        f"📅 {record['client']['date']}\\n"
                        f"⏰ {record['client']['time']}\\n"
                        f"💇 {record['client']['service']}\\n\\n"
                        f"*Какое поле меняем?*",
                        parse_mode='Markdown',
                        reply_markup=kb.edit_fields_keyboard())'''

content = content.replace(old_text, new_text)

with open('bot_core.py', 'w') as f:
    f.write(content)
print("✅ bot_core.py исправлен")
