import psutil

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hlink

from database.services import get_or_create_user_service, get_users_service

from functions.greeting import send_greeting

from elements.inline.other_inline import support_button
from elements.keybord.kb import cancel_kb
from events.states_group import Utils, Registration
from config.advertisement import support_link, ads_text

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
    if await state.get_state() is not None:
        await message.answer(
            text="🔎✨",
        )
        await state.clear()

    botname = message.bot.config['SETTINGS']['name']
    message_text = (
        f"<b>СПРАВКА {hlink(botname, 'https://t.me/+7gUBJMlHgPNkZmMy')}:</b>"
        f"\n\n1. Перед началом использования зарегистрируйтесь (/start), введя фамилию, имя и номер группы."
        f"\n2. Во время занятия бот пришлёт зарегистрированным пользователям кнопку проверки присутствия. Нажать её можно в течении часа."
        f"\n3. Отметиться можно раз в день (даже если вы придёте и утром, и вечером)."
        f"\n\nЧтобы связаться с поддержкой бота, присоединитесь к <b>{hlink('группе', support_link)}</b> и задайте вопрос в нужном топике."
        f"\n\n<i>{ads_text}</i>"
    )

    await message.answer(
        text=message_text,
        reply_markup=support_button().as_markup()
    )


# --- Отправка статистики --- #
@router.message(Command("bin"))
async def statistic_cmd(message: Message):    
    if int(message.chat.id) in map(int, message.bot.ADMIN_CHATS):
        users_data = await get_users_service()
        if users_data:
            users_count = f"<b>Пользователей:</b> <code>{len(users_data)}</code>"

            await message.answer(
                text=f"<b>СТАТИСТИКА:</b>\
                    \n\n{users_count}\
                    \n\n<b>CPU:</b> <code>{psutil.cpu_percent(interval=1)}</code> | <b>RAM:</b> <code>{psutil.virtual_memory().percent}</code>%\
                    \n<b>Использовано дискового пространства:</b> <code>{psutil.disk_usage('/').percent}</code>%"
            )


# --- Перейти в рассылку -> Написать текст --- #
@router.message(Command("mailing", "bin2"))
async def mailing_cmd(message: Message, state: FSMContext):
    if int(message.chat.id) in map(int, message.bot.ADMIN_CHATS):
        # Если стадия существует, выходим из неё
        if await state.get_state() is not None:
            await state.clear()

        await message.answer(
            text="💥 Введите <u>текст</u> или прикрепите <u>медиаконтент</u>, который будет отправлен всем пользователям:", 
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(Utils.mailing)
