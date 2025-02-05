import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from tortoise import Tortoise, run_async
from loguru import logger

from config.cfg import cfg, ADMIN_CHATS
from middleware.throttling import ThrottlingMiddleware 
from events import error_handler, states_group
from handlers import commands_handler
from handlers.utils import mailing

bot = Bot(
    token=cfg["SETTINGS"]["testing_token"], 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
bot.config = cfg
bot.ADMIN_CHATS = ADMIN_CHATS

dp = Dispatcher()


# --- Подгрузка модулей ТГ бота --- #
async def main():
    logger.info("Loading modules...")

    dp.include_routers(
        error_handler.router,
        states_group.router,
        commands_handler.router,
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
