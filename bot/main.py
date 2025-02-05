import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from tortoise import Tortoise, run_async
from loguru import logger

from config.cfg import cfg, ADMIN_CHATS
from middleware.throttling import ThrottlingMiddleware 
from events import error_handler, states_group
from handlers import commands_handler, registration, check
from handlers.utils import mailing
from functions.mailing import send_check_for_users
from functions.report import generate_attendance_report


bot = Bot(
    token=cfg["SETTINGS"]["token"], 
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
bot.config = cfg
bot.ADMIN_CHATS = ADMIN_CHATS
bot.ASSETS_PATH = "bot/assets/"
if not os.path.exists(bot.ASSETS_PATH):
    os.makedirs(bot.ASSETS_PATH)
    
storage = RedisStorage.from_url(url=cfg['SETTINGS']['redis_url'])
dp = Dispatcher(storage=storage)


# --- Ежедневная проверка и рассылка неактивным --- #
async def on_startup():
    scheduler = AsyncIOScheduler()
    # Запуск по четвергам в 09:10
    scheduler.add_job(
        func=send_check_for_users,
        trigger=CronTrigger(day_of_week='thu', hour=9, minute=10),
        kwargs={'bot': bot}
    )
    # Запуск по четвергам в 19:10
    scheduler.add_job(
        func=send_check_for_users,
        trigger=CronTrigger(day_of_week='thu', hour=19, minute=10),
        kwargs={'bot': bot}
    )
    # Запуск по четвергам в 20:10
    scheduler.add_job(
        func=generate_attendance_report,
        trigger=CronTrigger(day_of_week='thu', hour=20, minute=10),
        kwargs={'bot': bot}
    )
    scheduler.start()


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


# --- Функции для запуска --- #
async def startup():
    await on_startup()
    await main()


if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(startup())
