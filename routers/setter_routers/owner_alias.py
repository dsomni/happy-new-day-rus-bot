"""Contains owner_alias setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership


from settings import SETTINGS_MANAGER


router = Router()


class UpdateOwnerAlias(StatesGroup):
    """UpdateOwnerAlias FSA class"""

    update_alias = State()


@router.message(Command("set_owner_alias"))
@check_message_ownership
async def cmd_set_owner_alias(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_owner_alias command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Введите новый telegram alias")

    await state.set_state(UpdateOwnerAlias.update_alias)


@router.message(UpdateOwnerAlias.update_alias, F.text)
@check_message_ownership
async def owner_alias_update(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Second step of updating owner alias

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    tg_alias: str = message.text.strip()  # type: ignore
    if tg_alias.startswith("@"):
        tg_alias = tg_alias[1:]

    if len(tg_alias) == 0:
        await message.answer(
            text="Error: alias is empty",
        )
        return

    SETTINGS_MANAGER.set_owner_alias(tg_alias)

    await message.answer(
        text="Owner alias was successfully updated",
    )
    await state.clear()
