"""Contains developer action handlers"""

from aiogram import Bot, Router
from aiogram import types
from aiogram.filters.command import Command
from keyboards.basic import get_actions_markup, get_dev_actions_markup

from scheduler import SCHEDULER
from routers.utils import check_message_ownership


router = Router()


@router.message(Command("dev-actions"))
@check_message_ownership
async def cmd_dev_actions(
    message: types.Message, *args, **kwargs
):  # pylint: disable=W0613
    """/actions command handler

    Args:
        message (types.Message): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await message.answer(
        "Выберите действие", reply_markup=get_dev_actions_markup(user_id)
    )


@router.message(Command("scrap_n_post_sample"))
@check_message_ownership
async def cmd_scrap_n_post_sample(
    message: types.Message, bot: Bot, *args, **kwargs
):  # pylint: disable=W0613
    """scrap and post the sample entities to the owner

    Args:
        message (types.Mes sage): message object
    """

    user_id: int = message.from_user.id  # type: ignore

    await bot.send_message(user_id, "Start scrapping")
    await SCHEDULER.scrap_wrapper(force=True, limit=1)
    await message.answer("Scrapping was successfully finished ")

    await bot.send_message(user_id, "Start posting")
    await SCHEDULER.post_to_owner_wrapper()
    await message.answer("Posting was successfully finished ")
