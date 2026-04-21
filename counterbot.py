import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# Вставь свой токен здесь
TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_totals = {}

def extract_amount(text):
    text = text.lower()
    
    # 1. Ищем после "summasi:"
    # 2. Ищем перед "сум"
    patterns = [
        r'summasi:\s*([\d\s,.]+)',
        r'([\d\s,.]+)\s*сум'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).strip()
            
            # Очистка от всех видов пробелов
            amount_str = re.sub(r'\s+', '', amount_str)
            
            # Убираем точку в конце, если она там есть
            amount_str = amount_str.rstrip('.')

            # Логика для формата 12 000,00 или 12,000.00
            if ',' in amount_str and '.' in amount_str:
                # Если есть оба знака, считаем точку копейками (как в твоем чеке на 26к)
                # Значит запятую (разделитель тысяч) просто удаляем
                amount_str = amount_str.replace(',', '')
            
            # Если осталась только запятая, превращаем в точку для расчетов
            amount_str = amount_str.replace(',', '.')

            try:
                val = float(amount_str)
                return val
            except ValueError:
                continue
    return None

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    
    # Выводим итог красиво и сбрасываем
    # Форматируем число с пробелом между тысячами
    formatted_total = f"{total_sum:,.2f}".replace(',', ' ').replace('.', ',')
    
    await message.answer(f"📊 Итого: {formatted_total}\nСчетчик сброшен.")
    user_totals[user_id] = 0

@dp.message_handler()
async def handle_message(message: Message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    amount = extract_amount(message.text)
    
    if amount is not None:
        # Прибавляем к общей сумме
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        
        # Форматируем только число для ответа (убираем лишние нули после запятой, если это целое)
        if amount.is_integer():
            response = f"{int(amount):,}".replace(',', ' ')
        else:
            response = f"{amount:,.2f}".replace(',', ' ').replace('.', ',')
            
        # Бот отвечает только числом и всё
        await message.answer(response)

if __name__ == "__main__":
    print("Бот запущен. Жду чеки...")
    executor.start_polling(dp, skip_updates=True)
