import asyncio
import logging
import tgbot_config
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3

# Инициализация бота
bot = Bot(token=tgbot_config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()


# Обработка команды /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Hello! Enter the title of the book to purchase it.")


# Обработка введенного названия книги
@dp.message_handler()
async def get_book_info(message: types.Message):
    book_name = message.text

    # Запрос к базе данных
    cursor.execute("SELECT id, name, price, image_url, note FROM shop_product WHERE name=?", (book_name,))
    result = cursor.fetchone()

    if result is None:
        await message.reply("Book did not found.")
    else:
        book_id, book_name, book_price, book_image_url, book_note = result
        await buy(message, book_name, book_price, book_image_url, book_note)


async def buy(message: types.Message, title, price, photo_url, note):
    if tgbot_config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Test payment from the store.")

    labeled_price = types.LabeledPrice(label="Cost of book", amount=price * 100)

    await bot.send_invoice(message.chat.id,
                           title=title,
                           description=note,
                           provider_token=tgbot_config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url=photo_url,
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[labeled_price],
                           start_parameter="one-book-subscription",
                           payload="test-invoice-payload")


# Успешная оплата (должна ответить в течении 10 секунд)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# Успешная оплата
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Payment for the amount {message.successful_payment.total_amount // 100}"
                           f" {message.successful_payment.currency} was successful.")


# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(dp.start_polling())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(dp.storage.close())
        loop.run_until_complete(dp.storage.wait_closed())
        loop.close()
        cursor.close()
        conn.close()
