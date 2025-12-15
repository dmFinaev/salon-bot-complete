with open('bot_core.py', 'r') as f:
    lines = f.readlines()

# Исправляем строки 283-295
lines[282:295] = [
    '        bot.send_message(chat_id,\n',
    '                        f"✏️ *Редактирование записи #{number}:*\\\\n\\\\n"\n',
    '                        f"👤 {record[\\"client\\"][\\"name\\"]}\\\\n"\n',
    '                        f"📞 {record[\\"client\\"][\\"phone\\"]}\\\\n"\n',
    '                        f"📅 {record[\\"client\\"][\\"date\\"]}\\\\n"\n',
    '                        f"⏰ {record[\\"client\\"][\\"time\\"]}\\\\n"\n',
    '                        f"💇 {record[\\"client\\"][\\"service\\"]}\\\\n\\\\n"\n',
    '                        f"*Какое поле меняем?*",\n',
    '                        parse_mode=\'Markdown\',\n',
    '                        reply_markup=kb.edit_fields_keyboard())\n'
]

with open('bot_core.py', 'w') as f:
    f.writelines(lines)
print("✅ bot_core.py исправлен")
