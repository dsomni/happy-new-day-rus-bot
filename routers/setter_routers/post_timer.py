"""Contains post_timer setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership

from scheduler import SCHEDULER
from settings import SETTINGS_MANAGER


router = Router()


class UpdatePostTimer(StatesGroup):
    """UpdatePostTimer FSA class"""

    update_hours = State()
    update_minutes = State()


@router.message(Command("set_post_timer"))
@check_message_ownership
async def cmd_set_post_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_post_timer command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Введите час, когда будет производиться posting (0-23)")

    await state.set_state(UpdatePostTimer.update_hours)


@router.message(UpdatePostTimer.update_hours, F.text)
@check_message_ownership
async def post_timer_minutes(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Second step of updating post timer

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        hours = int(message.text.strip())  # type: ignore
        assert 0 <= hours <= 23
    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    await state.update_data(post_hours=hours)
    await message.answer(
        text="Введите минуты, когда будет производиться posting (0-59)"
    )
    await state.set_state(UpdatePostTimer.update_minutes)


@router.message(UpdatePostTimer.update_minutes, F.text)
@check_message_ownership
async def update_post_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating post timer

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        minutes = int(message.text.strip())  # type: ignore
        assert 0 <= minutes <= 59
    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    user_data = await state.get_data()

    hours = user_data["post_hours"]

    SETTINGS_MANAGER.set_post_timer(hours=hours, minutes=minutes)
    SCHEDULER.restart_post_job()

    await message.answer(
        text=f"Post timer was successfully updated to {hours}:{minutes}",
    )
    await state.clear()
