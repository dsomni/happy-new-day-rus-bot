"""Contains subscription handlers"""

# pylint: disable=import-error
from aiogram import Router
from aiogram.filters import Text
from aiogram import types

# pylint: enable=import-error

from keyboards.basic import get_basic_markup
from settings import SETTINGS_MANAGER


router = Router()


@router.message(Text("ПОДПИСАТЬСЯ"))
async def handle_subscribe(message: types.Message):
    """Text subscription handler

    Args:
        message (types.Message): message object
    """

    tg_id = message.from_user.id  # type: ignore
    tg_alias: str = message.from_user.username  # type: ignore

    SETTINGS_MANAGER.subscribe_user(tg_id, tg_alias)

    await message.answer(
        "Вы успешно подписались!", reply_markup=get_basic_markup(tg_id)
    )


@router.message(Text("ОТПИСАТЬСЯ"))
async def handle_unsubscribe(message: types.Message):
    """text unsubscribe handler

    Args:
        message (types.Message): message object
    """
    tg_id = message.from_user.id  # type: ignore

    SETTINGS_MANAGER.unsubscribe_user(tg_id)

    await message.answer("Вы успешно отписались!", reply_markup=get_basic_markup(tg_id))
