import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Хранилище сумм (по пользователям)
user_totals = {}

# Функция извлечения суммы
def extract_amount(text):
    match = re.search(r'([\d\s,\.]+)\s*сум', text.lower())
    if match:
        amount = match.group(1)
        amount = amount.replace(" ", "").replace(",", "")
        return float(amount)
    return None

# Обработка сообщений
@dp.message_handler()
async def handle_message(message: Message):
    user_id = message.from_user.id
    amount = extract_amount(message.text)

    if amount:
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        await message.reply(f"Добавлено: {int(amount)} сум\nТекущий баланс: {int(user_totals[user_id])} сум")

# Команда total
@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)

    await message.reply(f"Общая сумма: {int(total_sum)} сум")

    # сброс
    user_totals[user_id] = 0

# Запуск
if __name__ == "__main__":
    executor.start_polling(dp)