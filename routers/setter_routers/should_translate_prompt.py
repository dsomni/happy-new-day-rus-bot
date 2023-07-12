"""Contains should_translate_prompt setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership


from settings import SETTINGS_MANAGER


router = Router()


class UpdateShouldTranslatePrompt(StatesGroup):
    """UpdateSoftPrompt FSA class"""

    update_should_translate_prompt = State()


@router.message(Command("set_should_translate_prompt"))
@check_message_ownership
async def cmd_set_should_translate_prompt(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_should_translate_prompt command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Введите set_should_translate_prompt (1-True, 0-False)")

    await state.set_state(UpdateShouldTranslatePrompt.update_should_translate_prompt)


@router.message(UpdateShouldTranslatePrompt.update_should_translate_prompt, F.text)
@check_message_ownership
async def update_should_translate_promp(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating should_translate_prompt value

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        should_translate_prompt = bool(int(message.text.strip()))  # type: ignore

    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    SETTINGS_MANAGER.set_should_translate_prompt(
        should_translate_prompt=should_translate_prompt
    )

    await message.answer(
        text=f"Should_translate_prompt value was successfully updated to '{should_translate_prompt}'",
    )
    await state.clear()
