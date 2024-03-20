from aiogram import types
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class KeyboardFactory:
    @staticmethod
    async def create(buttons, back_data=None):
        keyboard = InlineKeyboardBuilder()
        for text, callback_data in buttons:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
            keyboard.row()
        if back_data:
            keyboard.add(InlineKeyboardButton(text="<<Назад", callback_data=back_data))
        keyboard.adjust(1)
        return keyboard

    @staticmethod
    async def generate_main_keyboard(buttons):
        keyboard = InlineKeyboardBuilder()
        for text, callback_data in buttons:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=callback_data))
        keyboard.adjust(1)
        return keyboard

    @staticmethod
    async def generate_static_keyboard(buttons):
        keyboard = ReplyKeyboardBuilder()
        for text in buttons:
            keyboard.add(types.KeyboardButton(text=text))
        return keyboard


# Используем фабрику клавиатур
keyboard_factory = KeyboardFactory()