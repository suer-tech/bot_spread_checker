import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
import psycopg2
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from app.services.repositories.entry_point_repositories import EntriesPointRepository
from app.services.repositories.percent_signal_repositories import PercentSignalRepository
from app.services.repositories.spread_repositories import SpreadRepository
from app.services.repositories.value_signal_repositories import ValueSignalRepository
from app.telegram.db import db
from app.telegram.keyboard.buttons import Button, main
from app.telegram.keyboard.keyboard import keyboard_factory
from app.telegram.states import TextSave


# Создание экземпляров бота и диспетчера
bot = Bot(token="6673857772:AAH4ZFcC9PFGSPs7o447QP_UQJNUiLjaVLw")
dp = Dispatcher()
previous_handler = None


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
    assets = await SpreadRepository.get_all_spreads()
    if len(assets) == 0:
        mess = "Сохраненные активы отсутствуют"
    else:
        mess = "Выберите актив:"
    # Добавление кнопок для каждого актива
    buttons = [(row[0], "asset_" + row[0]) for row in assets]
    # Создаем клавиатуру с активами
    keyboard = await keyboard_factory.create(buttons)
    # Отправляем сообщение с клавиатурой активов и ожидаем ответа
    await callback_query.message.edit_text(mess, reply_markup=keyboard.as_markup())


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
    spread_data = await SpreadRepository.get_spread_by_asset_name(asset_name)
    previous_keyboard = previous_handler
    mess = "Спред для {}: {}".format(asset_name, spread_data[0])
    await callback_query.message.answer(mess, reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Спреды"
@dp.callback_query(lambda c: c.data == 'show_spreads')
async def process_show_spreads(callback_query: types.CallbackQuery):
    assets = await SpreadRepository.get_all_spreads()
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
    assets = await EntriesPointRepository.get_all_entries_points()
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
    assets = await ValueSignalRepository.get_all_value_signals()
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
    assets = await PercentSignalRepository.get_all_percent_signals()
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
    entry_point = await EntriesPointRepository.get_entries_point_by_asset_name(asset_name)
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
    entry_point = await EntriesPointRepository.get_entries_point_by_asset_name(asset_name)
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
        query = EntriesPointRepository.add_entries_point(asset_name, new_entry)
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
    entry_point = await EntriesPointRepository.get_entries_point_by_asset_name(asset_name)
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
    reset = EntriesPointRepository.delete_entries_point(asset_name)
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
    current_value_signal = await ValueSignalRepository.get_value_signal_by_asset_name(asset_name)
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
    current_value_signal = await ValueSignalRepository.get_value_signal_by_asset_name(asset_name)
    if current_value_signal is not None:
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
        new_value_signal = float(message.text)
        data = await state.get_data()
        asset_name = data.get('asset_name')
        save_new_entry_point = await ValueSignalRepository.add_value_signal(asset_name, new_value_signal)
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
    current_value_signal = await ValueSignalRepository.get_value_signal_by_asset_name(asset_name)
    previous_keyboard = previous_handler
    if current_value_signal is not None:
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
    reset = await ValueSignalRepository.delete_value_signal(asset_name)
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
    current_percent_signal = await PercentSignalRepository.get_percent_signal_by_asset_name(asset_name)
    previous_keyboard = previous_handler
    if current_percent_signal is not None:
        await callback_query.message.edit_text(f"Сигнал по процентам для актива {asset_name}: {current_percent_signal}",
                                               reply_markup=previous_keyboard.as_markup())
    else:
        await callback_query.message.edit_text(f"Для актива {asset_name} нет сохраненного сигнала по процентам.",
                                               reply_markup=previous_keyboard.as_markup())


# Обработчик нажатия кнопки "Новый сигнал по значению"
@dp.callback_query(lambda c: c.data.startswith('new_percent_signal_'))
async def process_new_percent_signal_(callback_query: types.CallbackQuery, state: FSMContext):
    previous_keyboard = previous_handler
    asset_name = callback_query.data.split('_')[3]
    current_percent_signal = await PercentSignalRepository.get_percent_signal_by_asset_name(asset_name)
    if current_percent_signal is not None:
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
        new_percent_signal = float(message.text)
        data = await state.get_data()
        asset_name = data.get('asset_name')
        new_percent_signal = await PercentSignalRepository.add_percent_signal(asset_name, new_percent_signal)
        # Выводим сообщение об успешном сохранении новой точки входа
        mess = f"Новый сигнал по процентам для актива {asset_name} успешно сохранен: {new_percent_signal}"
        await message.answer(mess, reply_markup=previous_keyboard.as_markup())
        # Очищаем состояние
        await state.clear()
    except ValueError:
        await message.answer("Введено некорректное значение. Введите числовое значение.")


# Обработчик нажатия кнопки "Сбросить сигнал по процентам"
@dp.callback_query(lambda c: c.data.startswith('reset_percent_signal_'))
async def process_reset_percent_signal(callback_query: types.CallbackQuery):
    asset_name = callback_query.data.split('_')[3]
    current_percent_signal = await PercentSignalRepository.get_percent_signal_by_asset_name(asset_name)
    previous_keyboard = previous_handler
    if current_percent_signal is not None:
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
    reset = await PercentSignalRepository.delete_percent_signal(asset_name)
    if reset:
        # Отправляем сообщение об успешном сбросе сигнала
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
