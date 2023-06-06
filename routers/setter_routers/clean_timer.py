"""Contains clean_timer setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership

from scheduler import SCHEDULER
from settings import SETTINGS_MANAGER


router = Router()


class UpdateCleanTimer(StatesGroup):
    """UpdateCleanTimer FSA class"""

    update_days = State()


@router.message(Command("set_clean_timer"))
@check_message_ownership
async def cmd_set_clean_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_clean_timer command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(
        text="Введите раз во сколько дней нужно производить cleaning (1-inf)"
    )

    await state.set_state(UpdateCleanTimer.update_days)


@router.message(UpdateCleanTimer.update_days, F.text)
@check_message_ownership
async def update_clean_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating clean timer

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        days = int(message.text.strip())  # type: ignore
        assert days > 0
    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    SETTINGS_MANAGER.set_clean_timer(days=days)
    SCHEDULER.restart_clean_job()

    await message.answer(
        text=f"Clean timer was successfully updated to {days} days",
    )
    await state.clear()
