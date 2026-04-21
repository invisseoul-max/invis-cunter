import asyncio
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

# Твой токен от BotFather
TOKEN = "8606148076:AAFfNfFKAjq2YO6troH0Y70XxSWpI_O0Grk"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальная переменная для хранения суммы (в идеале использовать БД)
total_sum = 0.0

@dp.message(F.text)
async def handle_receipt(message: Message):
    global total_sum
    
    # Ищем строку вида "18 000,00 сум" или "18000 сум"
    # Регулярка ищет цифры, пробелы внутри числа и запятую
    match = re.search(r'([\d\s,]+)\s*сум', message.text)
    
    if match:
        # Извлекаем строку с числом
        amount_str = match.group(1).strip()
        
        try:
            # Очищаем строку: убираем пробелы и меняем запятую на точку для float
            clean_amount = amount_str.replace(' ', '').replace(',', '.')
            amount = float(clean_amount)
            
            total_sum += amount
            
            await message.reply(
                f"✅ Сумма принята: **{amount:,.2f} сум**\n"
                f"📊 Всего в копилке: **{total_sum:,.2f} сум**"
            )
        except ValueError:
            await message.reply("❌ Не удалось распознать формат суммы.")
    else:
        # Если это просто сообщение без суммы, игнорируем или даем подсказку
        pass

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

