from .models import User
from tortoise.transactions import atomic

@atomic()
async def get_users_service():
    """
    Получает всех пользователей из базы данных.

    Returns:
        list: Список словарей с идентификаторами пользователей.
    """
    users_data = await User.all()
    result = [{'user_id': entry.user_id} for entry in users_data]
    return result


@atomic()
async def get_or_create_user_service(user_id: int):
    """
    Получает пользователя по идентификатору или создает нового, если он не существует.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Словарь с идентификатором пользователя.
    """
    user_data = await User.get_or_none(user_id=user_id)
    if user_data is None:
        user_data = await User.create(user_id=user_id)

    return {'user_id': user_data.user_id}
