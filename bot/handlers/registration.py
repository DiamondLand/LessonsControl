import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from functions.formating import remove_inline_button
from elements.inline.other_inline import reg_button
from database.services import update_user_service

from events.states_group import not_in_state_filter, Registration

router = Router()


@router.message(Registration.name_lastname)
async def registration_name_lastname(message: Message, state: FSMContext):
    data = await state.get_data()
    # Используем регулярное выражение для удаления всех символов кроме русских букв
    # Разделяем строку на слова по пробелу, берём только первые два элемента (Иван Иванов)
    message_text = re.sub(r'[^а-яА-ЯёЁ]', '', message.text[:100])
    message_text = message.text.strip().split()
    if len(message_text) < 2:
        return await message.answer(text="Необходимо указать <b>два слова</b>: Имя и Фамилию:")

    firstname = message_text[0]
    lastname = message_text[1]

    if len(firstname) < 2:
        return await message.answer(text="Имя должно быть не короче <b>двух русских букв</b>:")
    if len(lastname) < 4:
        return await message.answer(text="Фамилия должна быть не короче <b>четырёх русских букв</b>:")

    data['firstname'] = firstname
    data['lastname'] = lastname
    await state.update_data(data)

    await message.answer(
        text=f"<b>Приятно познакомиться, <i>{firstname}</i> <i>{lastname}</i>!</b>\
            \nТеперь напишите в чат <b>только цифру</b> вашей группы. Например, <code>421</code>:"
    )
    await state.set_state(state=Registration.group)


@router.message(Registration.group)
async def registration_group(message: Message, state: FSMContext):
    # Оставляем только цифры
    group_number = re.sub(r'\D', '', message.text)
    if not group_number:
        return await message.answer(text="Введите только <b>цифры</b> вашей группы. Например, <u>421</u>:")

    data = await state.get_data()
    data['group_number'] = group_number
    await state.update_data(data)

    firstname = data.get('firstname')
    lastname = data.get('lastname')

    await message.answer(
        text=f"<b>Проверим данные, которые невозможно будет изменить!</b>\
            \n\nИмя: <code>{firstname}</code>\
            \nФамилия: <code>{lastname}</code>\
            \nГруппа: <code>{group_number}</code>\
            \n\n<i>❗ При нажатии на кнопку ниже, данные изменить больше не получится ❗</i>",
        reply_markup=reg_button().as_markup()
    )
    await state.set_state(state=Registration.save)


@router.callback_query(not_in_state_filter, (F.data.startswith("finish_registration")))
async def finish_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # Удаляем кнопку из сообщения
    await remove_inline_button(msg=callback.message)
    
    if not data:
        await callback.message.answer(
            text="<b>Данные не были сохранены ❗</b>\
                \nЧто-то пошло не так, воспользуйтесь /registration для повторной регистрации.",
            reply_markup=ReplyKeyboardRemove()
        )
        return await state.clear()

    firstname = data.get('firstname', None)
    lastname = data.get('lastname', None)
    group_number = data.get('group_number', None)

    await update_user_service(
        user_id=callback.from_user.id,
        firstname=firstname,
        lastname=lastname,
        group=group_number
    )

    await callback.message.answer(
        text="<b>Желаем успешного поступления!</b>\
            \n\n<i>Во время занятий (четверг с 9 до 10 с 19 до 20), в этом чате мы будем проводить перекличку.</i>",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
