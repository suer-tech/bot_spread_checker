import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
import psycopg2
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.telegram.db import db
from app.telegram.keyboard.buttons import Button, main
from app.telegram.keyboard.keyboard import keyboard_factory
from app.telegram.states import TextSave

# Создание экземпляров бота и диспетчера
bot = Bot(token="6673857772:AAH4ZFcC9PFGSPs7o447QP_UQJNUiLjaVLw")
dp = Dispatcher()
previous_handler = None


# ---------------------------------------------------------------------------------------------------------------------
#                                  Методы
# ---------------------------------------------------------------------------------------------------------------------
async def get_entry_point(asset_name, query):
    entry_point = None

    # Выполнение запроса к базе данных для получения списка активов
    entry_points = db.fetchall(query, (asset_name,))
    if len(entry_points) > 0:
        entry_point = entry_points[0][0]
    return entry_point


async def save_entry_point(asset_name, new_entry, query):
    try:
        # Выполнение SQL-запроса для вставки новой точки входа в таблицу entry_points
        db.execute(query, *(asset_name, new_entry))
        # Возвращаем True, чтобы указать, что точка входа успешно сохранена
        return True

    except (Exception, psycopg2.Error) as error:
        # В случае ошибки выводим сообщение об ошибке и возвращаем False
        print("Ошибка при сохранении:", error)
        return False


async def reset_entry_point(asset_name, query):
    try:
        # Выполнение SQL-запроса для удаления точки входа из таблицы entry_points
        db.execute(query, (asset_name,))
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
    static_buttons = await Button().static()
    static_keyboard = await keyboard_factory.generate_static_keyboard(static_buttons)
    await message.answer("Привет", reply_markup=static_keyboard.as_markup(resize_keyboard=True))


@dp.message()
async def check_rpm(message: types.Message):
    global previous_handler
    if message.text == 'Главное меню':
        main_buttons = await main()
        keyboard = await keyboard_factory.generate_main_keyboard(main_buttons)
        previous_handler = keyboard
        await message.answer("Выберите опцию:", reply_markup=keyboard.as_markup())



# Обработчик нажатия кнопки "Актив"
@dp.callback_query(lambda c: c.data == 'spreads')
async def process_assets(callback_query: types.CallbackQuery):
    assets = db.fetchall("SELECT asset_name FROM spreads")
    # Добавление кнопок для каждого актива
    buttons = [(row[0], "asset_" + row[0]) for row in assets]
    # Создаем клавиатуру с активами
    keyboard = await keyboard_factory.create(buttons)
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text("Выберите актив:", reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки актива
@dp.callback_query(lambda c: c.data.startswith('asset_'))
async def process_asset(callback_query: types.CallbackQuery):
    global previous_handler
    asset_name = callback_query.data.split('_')[1]
    buttons = await Button(asset_name).asset()
    keyboard = await keyboard_factory.create(buttons, back_data="spreads")
    previous_handler = keyboard
    # Отправляем сообщение с клавиатурой опций для актива и ожидаем ответа
    mess = "Выберите опцию для актива {}: ".format(asset_name)
    await callback_query.message.edit_text(mess, reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Спред"
@dp.callback_query(lambda c: c.data.startswith('spread_'))
async def process_spread(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[1]
    spread_data = db.fetchone("SELECT spread FROM spreads WHERE asset_name=%s", (asset_name,))
    previous_keyboard = previous_handler
    mess = "Спред для {}: {}".format(asset_name, spread_data[0])
    await callback_query.message.answer(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Спреды"
@dp.callback_query(lambda c: c.data == 'show_spreads')
async def process_show_spreads(callback_query: types.CallbackQuery):
    assets = db.fetchall("SELECT asset_name, spread FROM spreads")
    if assets:
        mess = '\n'.join([f'{row[0]}: {row[1]}' for row in assets])
    else:
        mess = "Спреды отсутствуют"
    previous_keyboard = previous_handler
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Точки входа"
@dp.callback_query(lambda c: c.data == 'entry_points')
async def process_show_entry_points(callback_query: types.CallbackQuery):
    assets = db.fetchall("SELECT asset_name, entry_point FROM entry_points")
    if assets:
        mess = '\n'.join([f'{row[0]}: {row[1]}' for row in assets])
    else:
        mess = "Точки входа отсутствуют"
    previous_keyboard = previous_handler
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Сигналы по значению"
@dp.callback_query(lambda c: c.data == 'value_signals')
async def process_show_value_signals(callback_query: types.CallbackQuery):
    assets = db.fetchall("SELECT asset_name, value_signal FROM value_signals")
    if assets:
        mess = '\n'.join([f'{row[0]}: {row[1]}' for row in assets])
    else:
        mess = "Сигналы по значению отсутствуют"
    previous_keyboard = previous_handler
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Сигналы по процентам"
@dp.callback_query(lambda c: c.data == 'percent_signals')
async def process_show_percent_signals(callback_query: types.CallbackQuery):
    assets = db.fetchall("SELECT asset_name, percent_signal FROM percent_signals")
    if assets:
        mess = '\n'.join([f'{row[0]}: {row[1]}' for row in assets])
    else:
        mess = "Сигналы по процентам отсутствуют"
    previous_keyboard = previous_handler
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text(mess, reply_markup=previous_keyboard.as_markup())


# ---------------------------------------------------------------------------------------------------------------------
#                                  Обработчики 'Точки входа'
# ---------------------------------------------------------------------------------------------------------------------


# Обработчик нажатия кнопки "Точка входа"
@dp.callback_query(lambda c: c.data.startswith('entry_point_'))
async def process_entry_point(callback_query: types.CallbackQuery):
    global previous_handler
    asset_name = callback_query.data.split('_')[2]
    buttons = await Button(asset_name).entry_point()
    keyboard = await keyboard_factory.create(buttons, back_data="spreads")
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
    buttons = await Button(asset_name).signals()
    keyboard = await keyboard_factory.create(buttons, back_data="spreads")
    previous_handler = keyboard
    await callback_query.message.edit_text("Выберите действие для сигнала актива {}: ".format(asset_name),
                                           reply_markup=keyboard.as_markup())


# Обработчик нажатия кнопки "Сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('valuesignals_'))
async def process_value_signals(callback_query: types.CallbackQuery):
    global previous_handler
    asset_name = callback_query.data.split('_')[1]
    buttons = await Button(asset_name).value_signals()
    keyboard = await keyboard_factory.create(buttons, back_data="signals_")
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
    buttons = await Button(asset_name).percent_signals()
    keyboard = await keyboard_factory.create(buttons, back_data="signals_")
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
