Понял тебя, это важный момент. Бот сейчас просто ищет цифры, не обращая внимания на статус операции. Чтобы он не считал «ошибочные» или «отмененные» чеки, нам нужно добавить проверку на «плохие» слова.

Я добавил список ключевых слов (Отменён, Ошибка, Не удалось), при наличии которых бот не будет прибавлять сумму, а напишет твою фразу.

Исправленный код:
Python
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
    text_lower = text.lower()
    
    # Список слов, при которых чек считать НЕЛЬЗЯ
    bad_words = ['отменён', 'отменен', 'ошибка', 'не удалось', 'произошла ошибка']
    
    # Если в тексте есть хоть одно "плохое" слово — возвращаем специальный флаг
    for word in bad_words:
        if word in text_lower:
            return "error_status"

    # Регулярки для поиска суммы
    patterns = [
        r'сумма:\s*([\d\s,.]+)',
        r'summasi:\s*([\d\s,.]+)',
        r'([\d\s,.]+)\s*сум'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).strip()
            amount_str = re.split(r'[^\d\s,.]', amount_str)[0].strip()
            amount_str = re.sub(r'\s+', '', amount_str)
            amount_str = amount_str.rstrip('.')

            if ',' in amount_str and '.' in amount_str:
                amount_str = amount_str.replace(',', '')
            
            amount_str = amount_str.replace(',', '.')

            try:
                return float(amount_str)
            except ValueError:
                continue
    return None

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    
    formatted_total = f"{total_sum:,.2f}".replace(',', ' ').replace('.', ',')
    await message.answer(f"📊 Итого: {formatted_total}\nСчетчик сброшен.")
    user_totals[user_id] = 0

@dp.message_handler()
async def handle_message(message: Message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    result = extract_amount(message.text)
    
    # Если статус чека плохой
    if result == "error_status":
        await message.answer("Не удалось извлечь сумму")
        return

    # Если сумма найдена
    if result is not None:
        user_totals[user_id] = user_totals.get(user_id, 0) + result
        
        # Форматируем для ответа
        if result.is_integer():
            response = f"{int(result):,}".replace(',', ' ')
        else:
            response = f"{result:,.2f}".replace(',', ' ').replace('.', ',')
            
        await message.answer(response)

if __name__ == "__main__":
    print("Бот запущен. Фильтрация ошибок включена.")
    executor.start_polling(dp, skip_updates=True)
