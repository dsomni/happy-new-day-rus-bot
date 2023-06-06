"""Contains scrap_timer setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership

from scheduler import SCHEDULER
from settings import SETTINGS_MANAGER


router = Router()


class UpdateScrapTimer(StatesGroup):
    """UpdateScrapTimer FSA class"""

    update_hours = State()
    update_minutes = State()


@router.message(Command("set_scrap_timer"))
@check_message_ownership
async def cmd_set_scrap_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_scrap_timer command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Введите час, когда будет производиться scrapping (0-23)")

    await state.set_state(UpdateScrapTimer.update_hours)


@router.message(UpdateScrapTimer.update_hours, F.text)
@check_message_ownership
async def scrap_timer_minutes(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Second step of updating scrap timer

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

    await state.update_data(scrap_hours=hours)
    await message.answer(
        text="Введите минуты, когда будет производиться scrapping (0-59)"
    )
    await state.set_state(UpdateScrapTimer.update_minutes)


@router.message(UpdateScrapTimer.update_minutes, F.text)
@check_message_ownership
async def update_scrap_timer(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating scrap timer

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

    hours = user_data["scrap_hours"]

    SETTINGS_MANAGER.set_scrap_timer(hours=hours, minutes=minutes)
    SCHEDULER.restart_scrap_job()

    await message.answer(
        text=f"Scrap timer was successfully updated to {hours}:{minutes}",
    )
    await state.clear()
