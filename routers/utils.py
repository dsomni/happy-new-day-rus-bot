"""Contains the utilities functions"""

from aiogram import types

from settings import SETTINGS_MANAGER


def check_message_ownership(func):
    """Checks the ownership of the user using message"""

    async def inner(*args, **kwargs):
        message: types.Message = args[0]
        tg_id: int = message.from_user.id  # type: ignore

        if not SETTINGS_MANAGER.is_owner(tg_id):
            return await message.answer("Недостаточно прав для выполнения команды (")

        return await func(*args, **kwargs)

    return inner
