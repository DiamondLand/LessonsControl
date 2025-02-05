import time

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.formating import remove_inline_button
from database.services import create_attendance_service

router = Router()


@router.callback_query(F.data.startswith("check_"))
async def check_in_func(callback: CallbackQuery, state: FSMContext):
    # Получаем timestamp из callback_data
    _, timestamp_str = callback.data.split("_")
    button_time = int(timestamp_str)
    current_time = int(time.time())  # Текущее время (UNIX timestamp)

    # Удаляем кнопку из сообщения
    await remove_inline_button(msg=callback.message)

    if current_time - button_time > 3600:  # 3600 секунд = 1 час
        return await callback.message.edit_text(
            text="<b>Время для отметки истекло ⏳</b>\
                \nВы можете отметить присутствие только в течение часа после начала занятия..."
        )

    # Записываем посещаемость
    result = await create_attendance_service(user_id=callback.from_user.id)
    if "error" in result:
        return await callback.message.edit_text(
            text=f"Здорово, что вы с нами, однако, {result['error'].lower()}"
        )

    await callback.message.edit_text(
        text=f"<b>Вы успешно отметились ✅</b>\
            \nВнимательно слушайте материал и не отвлекайтесь!"
    )
    await state.clear()
