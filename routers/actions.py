"""Contains developer action handlers"""

from aiogram import Bot, Router
from aiogram import types
from aiogram.filters.command import Command
from keyboards.basic import get_actions_markup

from scheduler import SCHEDULER
from routers.utils import check_message_ownership


router = Router()


@router.message(Command("actions"))
@check_message_ownership
async def cmd_actions(message: types.Message, *args, **kwargs):  # pylint: disable=W0613
    """/actions command handler

    Args:
        message (types.Message): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await message.answer("Выберите действие", reply_markup=get_actions_markup(user_id))


@router.message(Command("scrap"))
@check_message_ownership
async def cmd_scrap(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/scrap command handler

    Args:
        message (types.Mes sage): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start scrapping")
    await SCHEDULER.scrap_wrapper()
    await message.answer("Scrapping was successfully finished ")


@router.message(Command("scrap_force"))
@check_message_ownership
async def cmd_scrap_force(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/scrap command handler

    Args:
        message (types.Mes sage): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start force scrapping")
    await SCHEDULER.scrap_wrapper(force=True)
    await message.answer("Force scrapping was successfully finished ")


@router.message(Command("post"))
@check_message_ownership
async def cmd_post(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/post command handler

    Args:
        message (types.Mes sage): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start posting")
    await SCHEDULER.post_wrapper()
    await message.answer("Posting was successfully finished ")


@router.message(Command("post_to_owner"))
@check_message_ownership
async def cmd_post_to_owner(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/post_to_owner command handler

    Args:
        message (types.Mes sage): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start posting")
    await SCHEDULER.post_to_owner_wrapper()
    await message.answer("Posting was successfully finished ")


@router.message(Command("clean"))
@check_message_ownership
async def cmd_clean(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """/clean command handler

    Args:
        message (types.Mes sage): message object
    """
    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start cleaning")
    SCHEDULER.clean_wrapper()
    await message.answer("Cleaning was successfully finished ")
