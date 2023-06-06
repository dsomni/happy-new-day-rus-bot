"""Contains owner getters handlers"""

import asyncio
from aiogram import Bot, Router
from aiogram import types
from aiogram.filters.command import Command
from keyboards.basic import get_getters_markup
from routers.utils import check_message_ownership


from settings import SETTINGS_MANAGER


router = Router()


@router.message(Command("getters"))
@check_message_ownership
async def cmd_getters(message: types.Message, *args, **kwargs):  # pylint: disable=W0613
    """/getters command handler

    Args:
        message (types.Message): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await message.answer("Выберите параметр", reply_markup=get_getters_markup(user_id))


@router.message(Command("subscribers"))
@check_message_ownership
async def cmd_subscribers(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/subscribers command handler

    Args:
        message (types.Message): message object
        bot (types.Bot): bot object
    """

    subscribers = SETTINGS_MANAGER.subscribers
    user_id: int = message.from_user.id  # type: ignore

    for subscriber in subscribers:
        await bot.send_message(
            user_id,
            f"{subscriber.tg_id}\n@{subscriber.tg_alias}\n{subscriber.subscribe_date}",
        )
        await asyncio.sleep(0.5)


@router.message(Command("owner"))
@check_message_ownership
async def cmd_owner(message: types.Message, *args, **kwargs):  # pylint: disable=W0613
    """/owner command handler

    Args:
        message (types.Message): message object
    """

    owner = SETTINGS_MANAGER.owner

    await message.answer(f"{owner.tg_id}\n@{owner.tg_alias}")


@router.message(Command("timers"))
@check_message_ownership
async def cmd_timers(message: types.Message, *args, **kwargs):  # pylint: disable=W0613
    """/timers command handler

    Args:
        message (types.Message): message object
    """

    scrap_timer = SETTINGS_MANAGER.scrap_timer
    post_timer = SETTINGS_MANAGER.post_timer
    clean_timer = SETTINGS_MANAGER.clean_timer

    timers_text = ""
    timers_text += f"scrap_timer -- {scrap_timer.hours}:{scrap_timer.minutes}\n\n"
    timers_text += f"post_timer -- {post_timer.hours}:{post_timer.minutes}\n\n"
    timers_text += f"clean_timer -- {clean_timer.days} days\n\n"

    await message.answer(timers_text)


@router.message(Command("soft_prompt"))
@check_message_ownership
async def cmd_soft_prompt(
    message: types.Message, *args, **kwargs
):  # pylint: disable=W0613
    """/soft_prompt command handler

    Args:
        message (types.Message): message object
    """

    await message.answer(SETTINGS_MANAGER.image_soft_prompt)
