"""Contains image_styles setter router"""

from aiogram import F, Router
from aiogram import types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from routers.utils import check_message_ownership


from settings import SETTINGS_MANAGER


router = Router()


class UpdateImageStyles(StatesGroup):
    """UpdateImageStyles FSA class"""

    update_styles = State()


@router.message(Command("set_image_styles"))
@check_message_ownership
async def cmd_set_image_styles(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """/set_image_styles command handler

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    await message.answer(text="Список доступных стилей:")
    await message.answer(
        text=", ".join(SETTINGS_MANAGER.image_generator.available_styles)
    )
    await message.answer(text="Список текущих стилей:")
    await message.answer(text=", ".join(SETTINGS_MANAGER.image_generator.styles))

    await message.answer(text="Введите новый список стилей через запятую (english)")

    await state.set_state(UpdateImageStyles.update_styles)


@router.message(UpdateImageStyles.update_styles, F.text)
@check_message_ownership
async def update_image_styles(
    message: types.Message, state: FSMContext, *args, **kwargs
):  # pylint: disable=W0613
    """Final step of updating image styles

    Args:
        message (types.Message): message object
        state (types.FSMContext): FSA state
    """

    try:
        if message.text is None:
            message.text = ""
        image_styles = list(
            set(
                map(lambda w: w.strip(), message.text.strip().upper().split(",")),
            )
        )

    except BaseException:  # pylint: disable=W0718
        await message.answer(
            text="Error: input is unacceptable",
        )
        await state.clear()
        return

    if len(image_styles) == 0:
        image_styles = [""]

    SETTINGS_MANAGER.set_image_styles(styles=image_styles)

    await message.answer(
        text=f"Image styles were successfully updated to \n[{', '.join(image_styles)}]",
    )
    await state.clear()
