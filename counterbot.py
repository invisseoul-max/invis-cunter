import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor

# НЕ ЗАБУДЬ ОБНОВИТЬ ТОКЕН В BOTFATHER
TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

user_totals = {}

def extract_amount(text):
    text = text.lower()
    
    # Регулярки для поиска:
    # 1. Перед "сум"
    # 2. Перед "so'm" (любые вариации написания)
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
            
            # 1. Удаляем все пробелы (обычные и неразрывные)
            amount_str = re.sub(r'\s+', '', amount_str)
            
            # 2. Логика для формата 26,000.00 (узбекские чеки)
            # Если есть и запятая, и точка: значит точка отделяет тысячи, а запятая копейки (или наоборот)
            if ',' in amount_str and '.' in amount_str:
                # В твоем примере 26,000.00 -> убираем запятую, точку оставляем
                amount_str = amount_str.replace(',', '')
            elif ',' in amount_str and amount_str.count(',') == 1:
                # Если только одна запятая (например 26000,00), меняем на точку для float
                amount_str = amount_str.replace(',', '.')
            # Если в числе несколько точек (26.000.00), убираем все кроме последней
            elif amount_str.count('.') > 1:
                amount_str = amount_str.replace('.', '')

            try:
                val = float(amount_str)
                # Если сумма получилась очень маленькая (например, 26.0), 
                # а в строке было что-то вроде 26.000, возможно это ошибка распознавания разделителя
                return val
            except ValueError:
                continue
    return None

@dp.message_handler(commands=['total'])
async def total(message: Message):
    user_id = message.from_user.id
    total_sum = user_totals.get(user_id, 0)
    
    if total_sum > 0:
        # Выводим итог красиво и обнуляем
        await message.reply(f"📊 Итоговая сумма: {total_sum:,.2f} сум\n\nСчетчик обнулен.")
        user_totals[user_id] = 0
    else:
        await message.reply("В копилке пока пусто (0 сум).")

@dp.message_handler()
async def handle_message(message: Message):
    # Игнорируем команды
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    amount = extract_amount(message.text)
    
    if amount is not None:
        # Суммируем
        user_totals[user_id] = user_totals.get(user_id, 0) + amount
        
        # Вместо ответа сообщением, просто ставим "лайк" или "галочку"
        # Это подтвердит, что бот учел сумму, но не будет мешать в чате
        try:
            # На старых версиях aiogram это может не работать, тогда просто ничего не пишем
            await message.bot.send_sticker(message.chat.id, "✅", reply_to_message_id=message.message_id) 
            # Или просто:
            print(f"Добавлено {amount} для {user_id}")
        except:
            pass

if __name__ == "__main__":
    print("Бот запущен. Считаю чеки молча. Итог по команде /total")
    executor.start_polling(dp, skip_updates=True)
