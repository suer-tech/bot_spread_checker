from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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


# Используем фабрику клавиатур
keyboard_factory = KeyboardFactory()