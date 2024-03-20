import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
import psycopg2
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram.keyboard_buttons import Button
from app.telegram.states import TextSave

# Установка соединения с базой данных PostgreSQL
conn = psycopg2.connect(dbname='bot', user='postgres', password='password', host='localhost')
cursor = conn.cursor()

# Создание экземпляров бота и диспетчера
bot = Bot(token="5814873337:AAFmEDxaPRXmg8w1HQ4FTiNB1U5l8pgtFgE")
dp = Dispatcher()
router = Router()
previous_handler = None


# ---------------------------------------------------------------------------------------------------------------------
#                                  Методы
# ---------------------------------------------------------------------------------------------------------------------
async def create_keyboard(buttons, back_data=None):
    keyboard = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.row()
    if back_data:
        keyboard.add(InlineKeyboardButton(text="<<Назад", callback_data=back_data))
    keyboard.adjust(1)
    return keyboard


async def get_entry_point(asset_name, query):
    entry_point = None

    # Выполнение запроса к базе данных для получения списка активов
    cursor.execute(query, (asset_name,))
    entry_points = cursor.fetchall()
    if len(entry_points) > 0:
        entry_point = entry_points[0][0]
    return entry_point


async def save_entry_point(asset_name, new_entry, query):
    try:
        # Выполнение SQL-запроса для вставки новой точки входа в таблицу entry_points
        cursor.execute(query, (asset_name, new_entry))
        # Подтверждение изменений в базе данных
        conn.commit()
        # Возвращаем True, чтобы указать, что точка входа успешно сохранена
        return True

    except (Exception, psycopg2.Error) as error:
        # В случае ошибки выводим сообщение об ошибке и возвращаем False
        print("Ошибка при сохранении:", error)
        return False


async def reset_entry_point(asset_name, query):
    try:
        # Выполнение SQL-запроса для удаления точки входа из таблицы entry_points
        cursor.execute(query, (asset_name,))
        # Подтверждение изменений в базе данных
        conn.commit()
        # Возвращаем True, чтобы указать, что точка входа успешно удалена
        return True

    except (Exception, psycopg2.Error) as error:
        # В случае ошибки выводим сообщение об ошибке и возвращаем False
        print("Ошибка при сбросе:", error)
        return False


# ---------------------------------------------------------------------------------------------------------------------
#                                  Основные обработчики
# ---------------------------------------------------------------------------------------------------------------------

# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: types.Message):
    buttons = [("Актив", "spreads")]
    keyboard_markup = await create_keyboard(buttons)
    await message.answer("Выберите действие:", reply_markup=keyboard_markup.as_markup())


# Обработчик нажатия кнопки "Актив"
@dp.callback_query(lambda c: c.data == 'spreads')
async def process_assets(callback_query: types.CallbackQuery):
    cursor.execute("SELECT asset_name FROM spreads")
    assets = cursor.fetchall()

    # Добавление кнопок для каждого актива
    buttons = [(row[0], "asset_" + row[0]) for row in assets]
    # Создаем клавиатуру с активами
    keyboard_markup = await create_keyboard(buttons)
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text("Выберите актив:", reply_markup=keyboard_markup.as_markup())


# Обработчик нажатия кнопки актива
@dp.callback_query(lambda c: c.data.startswith('asset_'))
async def process_asset(callback_query: types.CallbackQuery):
    global previous_handler
    asset_name = callback_query.data.split('_')[1]
    buttons = Button(asset_name).asset()
    keyboard = await create_keyboard(buttons, back_data="spreads")
    previous_handler = keyboard
    # Отправляем сообщение с клавиатурой опций для актива и ожидаем ответа
    mess = "Выберите опцию для актива {}: ".format(asset_name)
    await callback_query.message.edit_text(mess, reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Спред"
@dp.callback_query(lambda c: c.data.startswith('spread_'))
async def process_spread(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    cursor.execute("SELECT spread FROM spreads WHERE asset_name=%s", (asset_name,))
    spread_data = cursor.fetchone()
    previous_keyboard = previous_handler
    mess = "Спред для {}: {}".format(asset_name, spread_data[0])
    await callback_query.message.answer(mess, reply_markup=previous_keyboard.as_markup())


# ---------------------------------------------------------------------------------------------------------------------
#                                  Обработчики 'Точки входа'
# ---------------------------------------------------------------------------------------------------------------------

# Обработчик нажатия кнопки "Точка входа"
@dp.callback_query(lambda c: c.data.startswith('entry_point_'))
async def process_entry_point(callback_query: types.CallbackQuery):
    global previous_handler

    asset_name = callback_query.data.split('_')[2]
    buttons = Button(asset_name).entry_point()
    keyboard = await create_keyboard(buttons, back_data="spreads")
    previous_handler = keyboard
    await callback_query.message.edit_text("Выберите действие для точки входа актива {}: ".format(asset_name),
                                           reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Текущая ТВХ"
@dp.callback_query(lambda c: c.data.startswith('current_entry_'))
async def process_current_entry(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[2]
    query = "SELECT entry_point FROM entry_points WHERE asset_name=%s"
    entry_point = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if entry_point is not None:
        await callback_query.message.edit_text(f"Текущая ТВХ для актива {asset_name}: {entry_point}",
                                               reply_markup=previous_keyboard.as_markup())
    else:
        await callback_query.message.edit_text(f"Для актива {asset_name} нет сохраненной точки входа.",
                                               reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Новая ТВХ"
@dp.callback_query(lambda c: c.data.startswith('new_entry_'))
async def process_new_entry(callback_query: types.CallbackQuery, state: FSMContext):
    previous_keyboard = previous_handler
    asset_name = callback_query.data.split('_')[2]
    query = "SELECT entry_point FROM entry_points WHERE asset_name=%s"
    entry_point = await get_entry_point(asset_name, query)
    if entry_point is not None:
        mess = f"Для актива {asset_name} уже существует точка входа."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
        return
    await callback_query.message.edit_text(f"Введите новую ТВХ для актива {asset_name}: ")
    # Устанавливаем состояние ожидания новой ТВХ
    await state.set_state(TextSave.waiting_for_entry)
    # Сохраняем информацию о текущем активе
    await state.update_data(asset_name=asset_name)


@dp.message(TextSave.waiting_for_entry)
async def process_new_entry_text(message: types.Message, state: FSMContext):
    previous_keyboard = previous_handler
    try:
        # Получаем введенное значение
        new_entry = float(message.text)
        # Получаем информацию о текущем активе из состояния
        data = await state.get_data()
        asset_name = data.get('asset_name')
        # Сохраняем новую ТВХ в базу данных
        query = "INSERT INTO entry_points (asset_name, entry_point) VALUES (%s, %s)"
        await save_entry_point(asset_name, new_entry, query)
        # Выводим сообщение об успешном сохранении новой точки входа
        mess = f"Новая ТВХ для актива {asset_name} успешно сохранена: {new_entry}"
        await message.answer(mess, reply_markup=previous_keyboard.as_markup())
        # Очищаем состояние
        await state.clear()
    except ValueError:
        await message.answer("Введено некорректное значение. Введите числовое значение.")


# Обработчик нажатия кнопки "Сбросить ТВХ"
@dp.callback_query(lambda c: c.data.startswith('reset_entry_'))
async def process_reset_entry(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[2]
    query = "SELECT entry_point FROM entry_points WHERE asset_name=%s"
    entry_point = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if entry_point is not None:
        # Создаем клавиатуру с кнопками "Да" и "Нет"
        confirm_keyboard = InlineKeyboardBuilder()
        confirm_keyboard.add(InlineKeyboardButton(text="Да", callback_data=f"confirm_reset_{asset_name}"))
        confirm_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=f"cancelreset_{asset_name}"))

        # Отправляем сообщение с вопросом о подтверждении сброса точки входа и клавиатурой для выбора "Да" или "Нет"
        mess = f"Вы уверены, что хотите сбросить ТВХ для актива {asset_name}?"
        await callback_query.message.edit_text(mess, reply_markup=confirm_keyboard.as_markup())
    else:
        mess = f"Для актива {asset_name} отсутствует сохраненная точка входа."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Да" для подтверждения сброса точки входа
@dp.callback_query(lambda c: c.data.startswith('confirm_reset_'))
async def process_confirm_reset(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[2]
    previous_keyboard = previous_handler
    # Выполняем сброс точки входа
    query = "DELETE FROM entry_points WHERE asset_name = %s"
    reset = await reset_entry_point(asset_name, query)
    if reset:
        # Отправляем сообщение об успешном сбросе точки входа
        mess = f"ТВХ для актива {asset_name} успешно сброшена."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
    else:
        mess = f"При сбросе ТВХ для актива {asset_name} произошла ошибка."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Нет" для отмены сброса точки входа
@dp.callback_query(lambda c: c.data.startswith('cancelreset_'))
async def process_cancel_reset(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    print(callback_query.data)
    # Возвращаемся к выбору опций для актива
    await process_asset(callback_query)


# ---------------------------------------------------------------------------------------------------------------------
#                                  Обработчики 'Сигналы'
# ---------------------------------------------------------------------------------------------------------------------
# Обработчик нажатия кнопки "Сигналы"
@dp.callback_query(lambda c: c.data.startswith('signals_'))
async def process_signals(callback_query: types.CallbackQuery):
    global previous_handler

    asset_name = callback_query.data.split('_')[1]
    buttons = Button(asset_name).signals()
    keyboard = await create_keyboard(buttons, back_data="spreads")
    previous_handler = keyboard
    await callback_query.message.edit_text("Выберите действие для сигнала актива {}: ".format(asset_name),
                                           reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('valuesignals_'))
async def process_value_signals(callback_query: types.CallbackQuery):
    global previous_handler

    asset_name = callback_query.data.split('_')[1]
    buttons = Button(asset_name).value_signals()
    keyboard = await create_keyboard(buttons, back_data="signals_")
    previous_handler = keyboard
    await callback_query.message.edit_text("Выберите действие для сигнала актива {}: ".format(asset_name),
                                           reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Текущий сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('current_value_signal_'))
async def process_current_value_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT value_signal FROM value_signals WHERE asset_name=%s"
    current_value_signal = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if current_value_signal is not None:
        await callback_query.message.edit_text(f"Сигнал по значению для актива {asset_name}: {current_value_signal}",
                                               reply_markup=previous_keyboard.as_markup())
    else:
        await callback_query.message.edit_text(f"Для актива {asset_name} нет сохраненного сигнала по значению.",
                                               reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Новый сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('new_value_signal_'))
async def process_new_value_signal(callback_query: types.CallbackQuery, state: FSMContext):
    previous_keyboard = previous_handler
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT value_signal FROM value_signals WHERE asset_name=%s"
    value_signal = await get_entry_point(asset_name, query)
    if value_signal is not None:
        mess = f"Для актива {asset_name} уже существует сигнал по значению."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
        return
    await callback_query.message.edit_text(f"Введите новый сигнал по значению для актива {asset_name}: ")
    # Устанавливаем состояние ожидания новой ТВХ
    await state.set_state(TextSave.waiting_for_value_signal)
    # Сохраняем информацию о текущем активе
    await state.update_data(asset_name=asset_name)


@dp.message(TextSave.waiting_for_value_signal)
async def process_new_value_signal_text(message: types.Message, state: FSMContext):
    previous_keyboard = previous_handler
    try:
        # Получаем введенное значение
        new_value_signal = float(message.text)
        # Получаем информацию о текущем активе из состояния
        data = await state.get_data()
        asset_name = data.get('asset_name')
        # Сохраняем новую ТВХ в базу данных
        query = "INSERT INTO value_signals (asset_name, value_signal) VALUES (%s, %s)"
        await save_entry_point(asset_name, new_value_signal, query)
        # Выводим сообщение об успешном сохранении новой точки входа
        mess = f"Новый сигнал по значению для актива {asset_name} успешно сохранен: {new_value_signal}"
        await message.answer(mess, reply_markup=previous_keyboard.as_markup())
        # Очищаем состояние
        await state.clear()
    except ValueError:
        await message.answer("Введено некорректное значение. Введите числовое значение.")


# Обработчик нажатия кнопки "Сбросить сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('reset_value_signal_'))
async def process_reset_value_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT value_signal FROM value_signals WHERE asset_name=%s"
    value_signal = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if value_signal is not None:
        # Создаем клавиатуру с кнопками "Да" и "Нет"
        confirm_keyboard = InlineKeyboardBuilder()
        confirm_keyboard.add(InlineKeyboardButton(text="Да", callback_data=f"confirm_value_signal_reset_{asset_name}"))
        confirm_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=f"cancelresetvaluesignal_{asset_name}"))

        # Отправляем сообщение с вопросом о подтверждении сброса точки входа и клавиатурой для выбора "Да" или "Нет"
        mess = f"Вы уверены, что хотите сбросить сигнал по значению для актива {asset_name}?"
        await callback_query.message.edit_text(mess, reply_markup=confirm_keyboard.as_markup())
    else:
        mess = f"Для актива {asset_name} отсутствует сохраненный сигнал по значению."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Да" для подтверждения сброса  сигнала по значению
@dp.callback_query(lambda c: c.data.startswith('confirm_value_signal_reset_'))
async def process_confirm_reset_value_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[4]
    previous_keyboard = previous_handler
    # Выполняем сброс точки входа
    query = "DELETE FROM value_signals WHERE asset_name = %s"
    reset = await reset_entry_point(asset_name, query)
    if reset:
        # Отправляем сообщение об успешном сбросе точки входа
        mess = f"Сигнал по значению для актива {asset_name} успешно сброшена."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
    else:
        mess = f"При сбросе сигнала по значению для актива {asset_name} произошла ошибка."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Нет" для отмены сброса  сигнала по значению
@dp.callback_query(lambda c: c.data.startswith('cancelresetvaluesignal_'))
async def process_cancel_reset_value_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    # Возвращаемся к выбору опций для актива
    await process_asset(callback_query)

# ---------------------------------------------------------------------------------------------------------------------
#                                  Обработчики 'Сигналы по процентам'
# ---------------------------------------------------------------------------------------------------------------------
# Обработчик нажатия кнопки "Сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('percentsignals_'))
async def process_percent_signals(callback_query: types.CallbackQuery):
    global previous_handler

    asset_name = callback_query.data.split('_')[1]
    buttons = Button(asset_name).percent_signals()
    keyboard = await create_keyboard(buttons, back_data="signals_")
    previous_handler = keyboard
    await callback_query.message.edit_text("Выберите действие для сигнала актива {}: ".format(asset_name),
                                           reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Сигнал по процентам"
@dp.callback_query(lambda c: c.data.startswith('current_percent_signal_'))
async def process_current_percent_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT percent_signal FROM percent_signals WHERE asset_name=%s"
    current_value_signal = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if current_value_signal is not None:
        await callback_query.message.edit_text(f"Сигнал по процентам для актива {asset_name}: {current_value_signal}",
                                               reply_markup=previous_keyboard.as_markup())
    else:
        await callback_query.message.edit_text(f"Для актива {asset_name} нет сохраненного сигнала по процентам.",
                                               reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Новый сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('new_percent_signal_'))
async def process_new_percent_signal_(callback_query: types.CallbackQuery, state: FSMContext):
    previous_keyboard = previous_handler
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT percent_signal FROM percent_signals WHERE asset_name=%s"
    value_signal = await get_entry_point(asset_name, query)
    if value_signal is not None:
        mess = f"Для актива {asset_name} уже существует сигнал по процентам."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
        return
    await callback_query.message.edit_text(f"Введите новый сигнал по процентам для актива {asset_name}: ")
    # Устанавливаем состояние ожидания новой ТВХ
    await state.set_state(TextSave.waiting_for_value_signal)
    # Сохраняем информацию о текущем активе
    await state.update_data(asset_name=asset_name)


@dp.message(TextSave.waiting_for_value_signal)
async def process_new_percent_signal_text(message: types.Message, state: FSMContext):
    previous_keyboard = previous_handler
    try:
        # Получаем введенное значение
        new_value_signal = float(message.text)
        # Получаем информацию о текущем активе из состояния
        data = await state.get_data()
        asset_name = data.get('asset_name')
        # Сохраняем новую ТВХ в базу данных
        query = "INSERT INTO percent_signals (asset_name, percent_signal) VALUES (%s, %s)"
        await save_entry_point(asset_name, new_value_signal, query)
        # Выводим сообщение об успешном сохранении новой точки входа
        mess = f"Новый сигнал по процентам для актива {asset_name} успешно сохранен: {new_value_signal}"
        await message.answer(mess, reply_markup=previous_keyboard.as_markup())
        # Очищаем состояние
        await state.clear()
    except ValueError:
        await message.answer("Введено некорректное значение. Введите числовое значение.")


# Обработчик нажатия кнопки "Сбросить сигнал по процентам"
@dp.callback_query(lambda c: c.data.startswith('reset_percent_signal_'))
async def process_reset_percent_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[3]
    query = "SELECT percent_signal FROM percent_signals WHERE asset_name=%s"
    value_signal = await get_entry_point(asset_name, query)
    previous_keyboard = previous_handler
    if value_signal is not None:
        # Создаем клавиатуру с кнопками "Да" и "Нет"
        confirm_keyboard = InlineKeyboardBuilder()
        confirm_keyboard.add(
            InlineKeyboardButton(text="Да", callback_data=f"confirm_percent_signal_reset_{asset_name}"))
        confirm_keyboard.add(InlineKeyboardButton(text="Нет", callback_data=f"cancepercentlreset_{asset_name}"))

        # Отправляем сообщение с вопросом о подтверждении сброса точки входа и клавиатурой для выбора "Да" или "Нет"
        mess = f"Вы уверены, что хотите сбросить сигнал по процентам для актива {asset_name}?"
        await callback_query.message.edit_text(mess, reply_markup=confirm_keyboard.as_markup())
    else:
        mess = f"Для актива {asset_name} отсутствует сохраненный сигнал по процентам."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Да" для подтверждения сброса  сигнала по процентам
@dp.callback_query(lambda c: c.data.startswith('confirm_percent_signal_reset_'))
async def process_confirm_reset_percent_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[4]
    previous_keyboard = previous_handler
    # Выполняем сброс точки входа
    query = "DELETE FROM percent_signals WHERE asset_name = %s"
    reset = await reset_entry_point(asset_name, query)
    if reset:
        # Отправляем сообщение об успешном сбросе точки входа
        mess = f"Сигнал по процентам для актива {asset_name} успешно сброшена."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())
    else:
        mess = f"При сбросе сигнала по процентам для актива {asset_name} произошла ошибка."
        await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Нет" для отмены сброса  сигнала по процентам
@dp.callback_query(lambda c: c.data.startswith('cancepercentlreset_'))
async def process_cancel_reset_percent_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    # Возвращаемся к выбору опций для актива
    await process_asset(callback_query)


start_bot = asyncio.run(dp.start_polling(bot))
