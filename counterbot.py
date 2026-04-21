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
    amount_str = None

    # 1. Ищем: "Сумма: 18 000"
    match_prefix = re.search(r'сумма:\s*([\d\s,\.]+)', text)
    # 2. Ищем: "18 000 сум"
    match_sum = re.search(r'([\d\s,\.]+)\s*сум', text)
    # 3. Ищем: "18 000 so\'m" (экранируем кавычку)
    match_som = re.search(r'([\d\s,\.]+)\s*so\'m', text)

    # Приоритет поиска
    if match_prefix:
        amount_str = match_prefix.group(1)
    elif match_sum:
        amount_str = match_sum.group(1)
    elif match_som:
        amount_str = match_som.group(1)

    if amount_str:
        # Очистка от всех видов пробелов и мусора
        amount_str = re.sub(r'\s+', '', amount_str)
        # Убираем лишние точки в конце, если они попали из предложения
        amount_str = amount_str.rstrip('.')
        
        # Обработка запятой как десятичного разделителя
        if ',' in amount_str:
            # Если есть и точка и запятая (1.200,50), убираем точку (разделитель тысяч)
            if '.' in amount_str:
                amount_str = amount_str.replace('.', '')
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
    
    if total_sum > 0:
        await message.reply(f"📊 Итоговая сумма: {total_sum:,.2f} сум\n\nСчетчик обнулен.")
        user_totals[user_id] = 0  # Вот здесь происходит обнуление
    else:
        await message.reply("В копилке пока пусто.")

@dp.message_handler()
async def handle_message(message: Message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    amount = extract_amount(message.text)
    
    if amount:
        # Просто прибавляем сумму, ничего не отвечая в чат
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        # Можно добавить реакцию (эмодзи), чтобы понимать, что чек принят
        try:
            await message.react([types.ReactionTypeEmoji(emoji="✅")])
        except:
            # Если версия телеграма/библиотеки не поддерживает реакции, просто игнорируем
            pass

if __name__ == "__main__":
    print("Бот запущен. Считаю чеки молча. Сброс и итог по команде /total")
    executor.start_polling(dp, skip_updates=True)
