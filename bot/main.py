import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from tortoise import Tortoise, run_async
from loguru import logger

from config.cfg import cfg, ADMIN_CHATS
from middleware.throttling import ThrottlingMiddleware 
from events import error_handler, states_group
from handlers import commands_handler, registration, check
from handlers.utils import mailing

bot = Bot(
    token=cfg["SETTINGS"]["token"], 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
bot.config = cfg
bot.ADMIN_CHATS = ADMIN_CHATS
bot.ASSETS_PATH = 'bot/assets/'  # Папка для сохранения файлов
if not os.path.exists(bot.ASSETS_PATH):
    os.makedirs(bot.ASSETS_PATH)
    
storage = RedisStorage.from_url(url=cfg['SETTINGS']['redis_url'])
dp = Dispatcher(storage=storage)


# --- Подгрузка модулей ТГ бота --- #
async def main():
    logger.info("Loading modules...")

    dp.include_routers(
        error_handler.router,
        states_group.router,
        commands_handler.router,
        registration.router,
        check.router,
        mailing.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Successfully launched")
    await dp.start_polling(bot)

# Подключаем ThrottlingMiddleware для всех роутеров
dp.message.middleware(ThrottlingMiddleware(limit=1, period=0.6))

# --- Подгрузка базы данных --- #
async def init_db():
    await Tortoise.init(
        db_url='sqlite://bot/database/database.db',
        modules={'models': ['database.models']}
    )
    await Tortoise.generate_schemas()

if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(main())
