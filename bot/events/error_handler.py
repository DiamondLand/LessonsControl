import os

from loguru import logger

# Настройка логирования
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logger.add(
    os.path.join(log_dir, '{time:YYYY-MM-DD}.json'), 
    rotation="1 day",  # Новый файл каждый день
    retention="30 days",  # Удаление файлов старше 30 дней
    level="WARNING",
    format="{time} {level} {message}",  # Формат записи
    serialize=True  # Запись в формате JSON
)

from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.exceptions import (
    AiogramError, TelegramAPIError, CallbackAnswerException, 
    SceneException, UnsupportedKeywordArgument,
    TelegramRetryAfter, TelegramMigrateToChat, 
    TelegramBadRequest, TelegramNotFound, TelegramConflictError,
    TelegramUnauthorizedError, TelegramForbiddenError, 
    TelegramServerError, RestartingTelegram, 
    TelegramEntityTooLarge, ClientDecodeError
)

router = Router()

# --- Обработчик ошибок ---
@router.error()
async def errors_handler(event: ErrorEvent):
    # Предупреждения
    if isinstance(event.exception, UnsupportedKeywordArgument):
        logger.warning(f"UnsupportedKeywordArgument: {event.exception}")

    elif isinstance(event.exception, TelegramBadRequest):
        logger.warning(f"TelegramBadRequest: {event.exception}")

    elif isinstance(event.exception, TelegramNotFound):
        logger.warning(f"TelegramNotFound: {event.exception}")

    elif isinstance(event.exception, TelegramConflictError):
        logger.warning(f"TelegramConflictError: {event.exception}")

    elif isinstance(event.exception, TelegramServerError):
        logger.warning(f"TelegramServerError: {event.exception}")
        
    elif isinstance(event.exception, CallbackAnswerException):
        logger.warning(f"CallbackException: {event.exception}")

    elif isinstance(event.exception, SceneException):
        logger.warning(f"SceneException: {event.exception}")

    elif isinstance(event.exception, TelegramRetryAfter):
        logger.warning(f"TelegramRetryAfter: {event.exception}")

    elif isinstance(event.exception, TelegramMigrateToChat):
        logger.warning(f"TelegramMigrateToChat: {event.exception}")

    elif isinstance(event.exception, TelegramForbiddenError):
        logger.warning(f"TelegramForbiddenError: {event.exception}")

    elif isinstance(event.exception, TelegramEntityTooLarge):
        logger.warning(f"TelegramEntityTooLarge: {event.exception}")

    elif isinstance(event.exception, ClientDecodeError):
        logger.warning(f"ClientDecodeError: {event.exception}")

    # Ошибки
    elif isinstance(event.exception, AiogramError):
        logger.error(f"AiogramError: {event.exception}")

    elif isinstance(event.exception, TelegramAPIError):
        logger.error(f"TelegramAPIError: {event.exception}")
    
    elif isinstance(event.exception, TelegramUnauthorizedError):
        logger.error(f"TelegramUnauthorizedError: {event.exception}")
    
    elif isinstance(event.exception, RestartingTelegram):
        logger.error(f"RestartingTelegram: {event.exception}")
