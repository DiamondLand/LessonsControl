from datetime import datetime


def send_greeting(username: str) -> str:
    current_time = datetime.now().time()

    if current_time.hour >= 4 and current_time.hour < 12:
        greeting = f"🌄 <b>Доброе утро, {f'{username}' if username else 'дорогой пользователь'}</b>!"
    elif current_time.hour >= 12 and current_time.hour < 18:
        greeting = f"⛅ <b>Добрый день, {f'{username}' if username else 'дорогой пользователь'}</b>!"
    elif current_time.hour >= 18 and current_time.hour < 23:
        greeting = f"🌇 <b>Добрый вечер, {f'{username}' if username else 'дорогой пользователь'}</b>!"
    else:
        greeting = f"🌃 <b>Доброй ночи, {f'{username}' if username else 'дорогой пользователь'}</b>!"

    return greeting
