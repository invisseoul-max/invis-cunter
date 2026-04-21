import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_totals = {}

def extract_amount(text):
    # Ищем цифры, пробелы, запятые или точки перед словом "сум"
    match = re.search(r'([\d\s,\.]+)\s*сум', text.lower())
    if match:
        amount_str = match.group(1)
        
        # 1. Удаляем ВСЕ виды пробелов (включая неразрывные \xa0)
        amount_str = re.sub(r'\s+', '', amount_str)
        
        # 2. Разбираемся с форматом 18.000,00 или 18,000.00
        # Если есть и запятая, и точка — убираем разделитель тысяч
        if ',' in amount_str and '.' in amount_str:
            amount_str = amount_str.replace(',', '') 
            
        # 3. Меняем запятую на точку (для float), если она осталась одна
        amount_str = amount_str.replace(',', '.')
        
        try:
            return float(amount_str)
        except ValueError:
            return None
    return None

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    await message.reply(f"📊 Общая сумма: {total_sum:,.2f} сум")
    # Если хочешь обнулять после команды /total:
    # user_totals[user_id] = 0

@dp.message_handler()
async def handle_message(message: Message):
    # Игнорируем команды, чтобы не двоилось
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    amount = extract_amount(message.text)
    
    if amount:
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        # Выводим красиво с разделением тысяч
        await message.reply(
            f"✅ Добавлено: {amount:,.2f} сум\n"
            f"💰 Текущий итог: {user_totals[user_id]:,.2f} сум"
        )

if __name__ == "__main__":
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
