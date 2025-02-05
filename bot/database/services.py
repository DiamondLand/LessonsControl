from datetime import date
from tortoise.transactions import atomic
from .models import User, Attendance


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
async def get_users_with_full_info_service():
    """
    Получает всех пользователей, у которых указаны все поля.

    Returns:
        list: Список пользователей с полными данными.
    """
    users_data = await User.filter(
        firstname__isnull=False, 
        lastname__isnull=False,
        group__isnull=False
        ).all()
    result = [
        {
            'user_id': entry.user_id,
            'firstname': entry.firstname,
            'lastname': entry.lastname,
            'group': entry.group
        }
        for entry in users_data
    ]
    
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
    user_data, created = await User.get_or_create(user_id=user_id)
    return user_data


@atomic()
async def update_user_service(user_id: int, firstname: str = None, lastname: str = None, group: int = None):
    """
    Обновляет имя и/или фамилию пользователя.

    Args:
        user_id (int): Идентификатор пользователя.
        firstname (str, optional): Имя.
        lastname (str, optional): Фамилия.
        group (int: optinal): Группа

    Returns:
        dict: Обновленный пользователь.
    """
    user = await User.get_or_none(user_id=user_id)
    if not user:
        return {'error': 'User not found'}

    if firstname:
        user.firstname = firstname
    if lastname:
        user.lastname = lastname
    if group:
        user.group = group

    await user.save()
    return {
        'user_id': user.user_id,
        'firstname': user.firstname,
        'lastname': user.lastname,
        'group': user.group
    }


@atomic()
async def create_attendance_service(user_id: int):
    """
    Регистрирует посещаемость пользователя на текущий день.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Сообщение об успешном создании или об ошибке.
    """
    user = await User.get_or_none(user_id=user_id)
    if not user:
        return {'error': 'User not found'}

    today = date.today()

    # Проверяем, есть ли уже запись на сегодня
    existing_attendance = await Attendance.get_or_none(user=user, date=today)
    if existing_attendance:
        return {'error': 'Attendance already recorded for today'}

    await Attendance.create(user=user, date=today)
    return {'message': 'Attendance recorded', 'user_id': user_id, 'date': today.isoformat()}


@atomic()
async def get_user_attendance_service(user_id: int, start_date: date, end_date: date):
    """
    Получает список посещаемости пользователя за указанный период.

    Args:
        user_id (int): Идентификатор пользователя.
        start_date (date): Начальная дата.
        end_date (date): Конечная дата.

    Returns:
        list: Список дат посещений.
    """
    user = await User.get_or_none(user_id=user_id)
    if not user:
        return {'error': 'User not found'}

    attendances = await Attendance.filter(user=user, date__range=[start_date, end_date]).values_list("date", flat=True)
    
    return {'user_id': user_id, 'attendances': [d.isoformat() for d in attendances]}


@atomic()
async def check_attendance_today(user_id: int):
    """
    Проверяет, есть ли у пользователя запись о посещении на сегодняшний день.

    Args:
        user_id (int): Идентификатор пользователя.

    Returns:
        dict: Информация о наличии посещения.
    """
    user = await User.get_or_none(user_id=user_id)
    if not user:
        return {'error': 'User not found'}

    today = date.today()
    attendance = await Attendance.get_or_none(user=user, date=today)

    return {'user_id': user_id, 'has_attended_today': attendance is not None}
