"""Contains soft_prompt setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership


from settings import SETTINGS_MANAGER


router = Router()


class UpdateSoftPrompt(StatesGroup):
    """UpdateSoftPrompt FSA class"""

    update_prompt = State()


@router.message(Command("set_soft_prompt"))
@check_message_ownership
async def cmd_set_soft_prompt(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_soft_prompt command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Введите новый soft_prompt (english)")

    await state.set_state(UpdateSoftPrompt.update_prompt)


@router.message(UpdateSoftPrompt.update_prompt, F.text)
@check_message_ownership
async def update_soft_prompt(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating image soft prompt

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        soft_prompt = message.text.strip()  # type: ignore

    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    SETTINGS_MANAGER.set_image_soft_prompt(prompt=soft_prompt)

    await message.answer(
        text=f"Soft prompt was successfully updated to '{soft_prompt}'",
    )
    await state.clear()
