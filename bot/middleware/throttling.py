import random

from typing import Callable, Awaitable, Dict, Any
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: int, period: float) -> None:
        self.limit = limit
        self.period = timedelta(seconds=period)
        self.timestamps = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        # Если отправлено в канале или группе, то не реагируем
        if event.chat.type in ['channel', 'group', 'supergroup']:
            return None

        now = datetime.now()
        user_id = event.from_user.id
        
        if user_id not in self.timestamps:
            self.timestamps[user_id] = now
            
        # Если прошло меньше периода, отклоняем событие
        elif (now - self.timestamps[user_id]) < self.period:
            await event.answer(text=f"Слишком быстро, повторите через <code>0.{random.randint(5, 8)}</code> секунд ❗")
            return None

        # Обновляем временную метку последнего события
        self.timestamps[user_id] = now

        return await handler(event, data)