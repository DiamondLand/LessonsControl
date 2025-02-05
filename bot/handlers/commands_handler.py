from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink

from database.services import get_or_create_user_service

from functions.greeting import send_greeting
from functions.mailing import send_check_for_users

from elements.inline.other_inline import support_button
from elements.keybord.kb import cancel_kb
from events.states_group import Utils, Registration
from config.advertisement import support_link

router = Router()


# --- Основная панель --- #
@router.message(Command("start", "registration"))
async def start_cmd(message: Message, state: FSMContext):
    user_data = await get_or_create_user_service(
        user_id=message.from_user.id
    )
    if user_data and user_data.firstname and user_data.lastname:
        return await message.answer(
            text=f"{send_greeting(username=user_data.firstname)}\
                \nПреподаватель проведёт перекличку через этого бота во время проведения занятий, не теряйтесь 💤!"
            )
    await message.answer(
        text=f"{send_greeting(username=message.from_user.first_name)}\
            \nДля контроля посещаемости необходимо указать <b>имя</b> и <b>фамилию</b>, разделяя пробелом:\
            \n\n<i>❗ Изменить эти данные будет нельзя. Перепроверьте всё несколько раз ❗</i>",
        reply_markup=cancel_kb()
    )
    await state.set_state(state=Registration.name_lastname)


# --- Информационнная панель --- #
@router.message(Command("info"))
async def info_cmd(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    await send_check_for_users(message.bot)
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
