import asyncio
import aiogram
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import psycopg2
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Установка соединения с базой данных PostgreSQL
conn = psycopg2.connect(dbname='bot', user='postgres', password='password', host='localhost')
cursor = conn.cursor()

# Создание экземпляров бота и диспетчера
bot = Bot(token="5814873337:AAFmEDxaPRXmg8w1HQ4FTiNB1U5l8pgtFgE")
dp = Dispatcher()


# Функция для создания встроенной клавиатуры
def create_inline_keyboard():
    builder = InlineKeyboardBuilder()

    # Добавляем кнопку "Актив"
    builder.button(text="Актив", callback_data="assets")

    # Приводим клавиатуру к формату (1 строка, 1 кнопка)
    builder.adjust(1, 1)

    # Возвращаем собранную клавиатуру
    return builder.as_markup()


# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard_markup = create_inline_keyboard()

    await message.answer("Выберите действие:", reply_markup=keyboard_markup)


# Функция для создания клавиатуры с активами
async def create_assets_keyboard():
    builder = InlineKeyboardBuilder()

    # Выполнение запроса к базе данных для получения списка активов
    cursor.execute("SELECT asset_name FROM assets")
    assets = cursor.fetchall()

    # Добавление кнопок для каждого актива
    for row in assets:
        builder.button(text=row[0], callback_data="asset_" + row[0])

    builder.adjust(1)
    # Возвращаем собранную клавиатуру
    return builder.as_markup()


# Обработчик нажатия кнопки "Актив"
@dp.callback_query(lambda c: c.data == 'assets')
async def process_assets(callback_query: types.CallbackQuery):
    # Создаем клавиатуру с активами
    assets_keyboard = await create_assets_keyboard()

    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text("Выберите актив:", reply_markup=assets_keyboard)


# Обработчик нажатия кнопки актива
@dp.callback_query(lambda c: c.data.startswith('asset_'))
async def process_asset(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    asset_options_keyboard = types.InlineKeyboardMarkup()
    asset_options_keyboard.add(InlineKeyboardButton(text="Спред", callback_data="spread_" + asset_name))
    asset_options_keyboard.add(InlineKeyboardButton(text="Точка входа", callback_data="entry_point_" + asset_name))
    # Добавьте другие кнопки по желанию
    await callback_query.message.edit_text("Выберите опцию для актива {}: ".format(asset_name),
                                           reply_markup=asset_options_keyboard)


# Обработчик нажатия кнопки "Спред"
@dp.callback_query(lambda c: c.data.startswith('spread_'))
async def process_spread(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    cursor.execute("SELECT spread FROM spreads WHERE asset_name=%s", (asset_name,))
    spread_data = cursor.fetchone()
    await callback_query.message.answer("Спред для {}: {}".format(asset_name, spread_data[0]))


# Обработчик нажатия кнопки "Точка входа"
@dp.callback_query(lambda c: c.data.startswith('entry_point_'))
async def process_entry_point(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    entry_point_keyboard = types.InlineKeyboardMarkup()
    entry_point_keyboard.add(InlineKeyboardButton(text="Текущая ТВХ", callback_data="current_entry_" + asset_name))
    entry_point_keyboard.add(InlineKeyboardButton(text="Новая ТВХ", callback_data="new_entry_" + asset_name))
    entry_point_keyboard.add(InlineKeyboardButton(text="Сбросить ТВХ", callback_data="reset_entry_" + asset_name))
    await callback_query.message.edit_text("Выберите действие для точки входа актива {}: ".format(asset_name),
                                           reply_markup=entry_point_keyboard)


# Добавьте другие обработчики кнопок по мере необходимости


start_bot = asyncio.run(dp.start_polling(bot))
