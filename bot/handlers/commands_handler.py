from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink

from database.services import get_or_create_user_service

from functions.greeting import send_greeting

from elements.inline.other_inline import support_button
from events.states_group import Utils
from config.advertisement import support_link

router = Router()


# --- Основная панель --- #
@router.message(Command("start"))
async def start_cmd(message: Message, state: FSMContext):
    try:
        await get_or_create_user_service(user_id=message.from_user.id)
    except Exception as _ex:
        logger.debug(f"Не удалось проверить аккаунт: {_ex}")

    await message.answer(
        text=f"{send_greeting(username=message.from_user.first_name)}"
    )


# --- Информационнная панель --- #
@router.message(Command("info"))
async def info_cmd(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await message.answer(
            text="🔎✨",
        )
        await state.clear()

    botname = message.bot.config['SETTINGS']['name']
    message_text = (
        f"<b>СПРАВКА {hlink(botname, support_link)} v{message.bot.config['SETTINGS']['version']}:</b>"
        f"\n\n Чтобы связаться с поддержкой бота, присоединитесь к <b>{hlink('группе', support_link)}</b> и задайте вопрос в нужном топике."
    )

    await message.answer(
        text=message_text,
        reply_markup=support_button().as_markup()
    )


# --- Перейти в рассылку -> Написать текст --- #
@router.message(Command("mailing", "bin2"))
async def mailing_cmd(message: Message, state: FSMContext):
    if int(message.chat.id) in map(int, message.bot.ADMIN_GROUP):
        # Если стадия существует, выходим из неё
        if await state.get_state() is not None:
            await state.clear()

        await message.answer(
            text="💥 Введите <u>текст</u> или прикрепите <u>медиаконтент</u>, который будет отправлен всем пользователям:", 
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Utils.mailing)
