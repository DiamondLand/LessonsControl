from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.advertisement import support_link


def support_button() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Поддержка",
            url=support_link,
            callback_data="connect_with_support"
        )
    )
    return builder


def reg_button() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Всё верно 💚",
            callback_data="finish_registration"
        )
    )
    return builder
