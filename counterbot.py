import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_totals = {}

def extract_amount(text):
    text = text.lower()
    
    # Регулярки для разных сценариев:
    # 1. Перед "сум"
    # 2. Перед "so'm" (учитываем возможные пробелы: so ' m, som, so'm)
    # 3. После "сумма:"
    patterns = [
        r'([\d\s,.]+)\s*сум',
        r'([\d\s,.]+)\s*so\s*\'?\s*m',
        r'сумма:\s*([\d\s,.]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).strip()
            
            # Чистим от неразрывных пробелов (\xa0) и обычных пробелов
            amount_str = re.sub(r'\s+', '', amount_str)
            # Убираем точку в конце, если она попала случайно
            amount_str = amount_str.rstrip('.')
            
            # Обработка разделителей
            if ',' in amount_str:
                if '.' in amount_str: 
                    amount_str = amount_str.replace('.', '') # 1.000,00 -> 1000,00
                amount_str = amount_str.replace(',', '.')    # 1000,00 -> 1000.00
            
            try:
                return float(amount_str)
            except ValueError:
                continue
    return None

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    
    if total_sum > 0:
        # Выводим итог и обнуляем
        await message.reply(f"📊 Итоговая сумма: {total_sum:,.2f} сум\n\nСчетчик обнулен.")
        user_totals[user_id] = 0
    else:
        await message.reply("В копилке 0 сум.")

@dp.message_handler()
async def handle_message(message: Message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    amount = extract_amount(message.text)
    
    if amount is not None:
        # Плюсуем в базу
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        
        # Отвечаем только найденным числом (красиво отформатированным)
        # Если хочешь без копеек, можно использовать int(amount)
        formatted_amount = f"{amount:,.2f}".replace(',', ' ').replace('.', ',')
        await message.reply(formatted_amount)

if __name__ == "__main__":
    print("Бот работает...")
    executor.start_polling(dp, skip_updates=True)
