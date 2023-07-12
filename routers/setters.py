"""Contains owner setters handlers"""

from aiogram import Router
from aiogram import types
from aiogram.filters.command import Command


from keyboards.basic import get_setters_markup
from routers.utils import check_message_ownership

from routers.setter_routers import (
    owner_alias,
    scrap_timer,
    post_timer,
    clean_timer,
    soft_prompt,
    should_translate_prompt,
)


router = Router()

router.include_routers(
    owner_alias.router,
    scrap_timer.router,
    post_timer.router,
    clean_timer.router,
    soft_prompt.router,
    should_translate_prompt.router,
)


@router.message(Command("setters"))
@check_message_ownership
async def cmd_setters(message: types.Message, *args, **kwargs):  # pylint: disable=W0613
    """/setters command handler

    Args:
        message (types.Message): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await message.answer(
        "Выберите параметр для редактирования", reply_markup=get_setters_markup(user_id)
    )
