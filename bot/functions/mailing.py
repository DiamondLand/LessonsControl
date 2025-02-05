from aiogram import Bot

from elements.inline.other_inline import check_button
from database.services import get_users_with_full_info_service


async def send_check_for_users(bot: Bot):
    """
    Отправляет сообщение с кнопкой 'Присутствую ✅'.
    
    Args:
        bot (Bot): Объект бота для отправки сообщений.
    """
    users = await get_users_with_full_info_service()  # Получаем список пользователей
    for user in users:
        user_id = user.get('user_id')
        if not user_id:
            continue  # Пропускаем, если нет user_id

        text = "Перекличка! Вы на занятии ⁉"

        try:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=check_button().as_markup(),
                parse_mode="HTML"
            )
        except:
            pass
