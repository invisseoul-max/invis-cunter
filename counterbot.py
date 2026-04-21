import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# Вставь свой токен сюда
TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Словарь для хранения итогов (сбрасывается при перезагрузке)
user_totals = {}

def extract_amount(text):
    text_lower = text.lower()
    
    # 1. Проверка на статус чека (если плохой — игнорируем)
    bad_words = ['отменён', 'отменен', 'ошибка', 'не удалось', 'произошла ошибка', 'отказано']
    for word in bad_words:
        if word in text_lower:
            return "error_status"

    # 2. Регулярки для поиска суммы
    patterns = [
        r'сумма:\s*([\d\s,.]+)', # После "Сумма:"
        r'summasi:\s*([\d\s,.]+)', # После "summasi:"
        r'([\d\s,.]+)\s*сум',      # Перед "сум"
        r'([\d\s,.]+)\s*so\s*\'?\s*m' # Перед "so'm"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).strip()
            # Убираем лишний текст, если он приклеился (берем только цифры/точки/запятые)
            amount_str = re.split(r'[^\d\s,.]', amount_str)[0].strip()
            # Удаляем все пробелы
            amount_str = re.sub(r'\s+', '', amount_str)
            # Убираем точку в конце (если это конец предложения)
            amount_str = amount_str.rstrip('.')

            # Исправляем форматы: 12,000.00 или 12 000,00
            if ',' in amount_str and '.' in amount_str:
                amount_str = amount_str.replace(',', '')
            
            amount_str = amount_str.replace(',', '.')

            try:
                return float(amount_str)
            except ValueError:
                continue
    return None

def format_number(num):
    """Красиво форматирует число: 300 000 вместо 300000.00"""
    if num % 1 == 0:
        return f"{int(num):,}".replace(',', ' ')
    else:
        return f"{num:,.2f}".replace(',', ' ').replace('.', ',')

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    
    if total_sum > 0:
        formatted = format_number(total_sum)
        await message.answer(f"📊 Итоговая сумма: {formatted}\nСчетчик сброшен.")
        user_totals[user_id] = 0
    else:
        await message.answer("Сумма пока равна 0.")

@dp.message_handler()
async def handle_message(message: Message):
    # Игнорируем команды
    if message.text and message.text.startswith('/'):
        return

    user_id = message.from_user.id
    result = extract_amount(message.text)
    
    # Если в чеке ошибка
    if result == "error_status":
        await message.answer("Не удалось извлечь сумму")
        return

    # Если сумма успешно найдена
    if result is not None:
        user_totals[user_id] = user_totals.get(user_id, 0) + result
        
        # Отвечаем только чистым числом
        await message.answer(format_number(result))

if __name__ == "__main__":
    print("Бот запущен. Считаю только успешные чеки.")
    executor.start_polling(dp, skip_updates=True)
