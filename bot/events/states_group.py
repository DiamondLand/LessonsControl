from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from elements.keybord.kb import cancel

router = Router()


class Registration(StatesGroup):
    name_lastname = State()
    group = State()
    save = State()


class Utils(StatesGroup):
    mailing = State()


not_in_state_filter = ~StateFilter(
    Utils.mailing,
    Registration.name_lastname,
    Registration.group,
)


# --- Завершение заполнения формы --- #
@router.message(F.text == cancel)
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Запись текста прервана ❗", 
        reply_markup=ReplyKeyboardRemove()
    )
