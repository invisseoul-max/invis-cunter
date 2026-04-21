import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# НЕ ЗАБУДЬ ОБНОВИТЬ ТОКЕН
TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_totals = {}

def extract_amount(text):
    text = text.lower()
    
    # 1. Ищем после "сумма:" до конца строки или до ближайшего слова
    # 2. Ищем после "summasi:"
    # 3. Ищем перед "сум"
    patterns = [
        r'сумма:\s*([\d\s,.]+)',
        r'summasi:\s*([\d\s,.]+)',
        r'([\d\s,.]+)\s*сум'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            amount_str = match.group(1).strip()
            
            # Убираем всё лишнее, кроме цифр, точек и запятых
            # Это удалит перенос строки, если сумма была в конце заголовка
            amount_str = re.split(r'[^\d\s,.]', amount_str)[0].strip()
            
            # Очистка от всех видов пробелов
            amount_str = re.sub(r'\s+', '', amount_str)
            # Убираем точку в конце (пунктуация)
            amount_str = amount_str.rstrip('.')

            # Исправляем логику разделителей для узбекских чеков
            if ',' in amount_str and '.' in amount_str:
                # Например: 26,000.00 -> удаляем запятую
                amount_str = amount_str.replace(',', '')
            
            # Если запятая одна (100,00), делаем её точкой для расчетов
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
    
    # Форматируем итог с пробелом в тысячах
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
        # Плюсуем
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        
        # Бот отвечает ТОЛЬКО числом (без копеек, если сумма целая)
        if amount.is_integer():
            response = f"{int(amount):,}".replace(',', ' ')
        else:
            response = f"{amount:,.2f}".replace(',', ' ').replace('.', ',')
            
        await message.answer(response)

if __name__ == "__main__":
    print("Бот запущен. Теперь видит чеки с 'Сумма:'")
    executor.start_polling(dp, skip_updates=True)
